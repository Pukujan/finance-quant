using System.Globalization;
using System.Text.Json;
using QuantConnect;
using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Interfaces;
using QuantConnect.Orders;
using QuantConnect.Orders.Fills;
using QuantConnect.Securities;
using QuantConnect.Securities.Equity;

sealed class SingleConfigProvider : ISubscriptionDataConfigProvider
{
    private readonly List<SubscriptionDataConfig> _configs;

    public SingleConfigProvider(SubscriptionDataConfig config)
    {
        _configs = new List<SubscriptionDataConfig> { config };
    }

    public List<SubscriptionDataConfig> GetSubscriptionDataConfigs(Symbol symbol = null, bool includeInternalConfigs = false)
    {
        if (symbol is null)
        {
            return new List<SubscriptionDataConfig>(_configs);
        }
        return _configs.Where(config => config.Symbol == symbol).ToList();
    }
}

static class Program
{
    private static SecurityExchangeHours CreateWeekdayHours()
    {
        var hours = Enum.GetValues<DayOfWeek>().ToDictionary(
            day => day,
            day => day is DayOfWeek.Saturday or DayOfWeek.Sunday
                ? LocalMarketHours.ClosedAllDay(day)
                : new LocalMarketHours(day, TimeSpan.FromHours(9.5), TimeSpan.FromHours(16)));
        return new SecurityExchangeHours(
            TimeZones.NewYork,
            Array.Empty<DateTime>(),
            hours,
            new Dictionary<DateTime, TimeSpan>(),
            new Dictionary<DateTime, TimeSpan>());
    }

    private static DateTime ParseUtc(string value)
    {
        return DateTimeOffset.Parse(
            value,
            CultureInfo.InvariantCulture,
            DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal).UtcDateTime;
    }

    public static int Main(string[] args)
    {
        if (args.Length != 1)
        {
            Console.Error.WriteLine("usage: LeanA1Probe <fixture.json>");
            return 2;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(args[0]));
        var root = document.RootElement;
        var intents = root.GetProperty("intents");
        if (intents.GetArrayLength() != 1)
        {
            throw new InvalidOperationException("probe requires exactly one intent");
        }
        var intent = intents[0];
        var events = root.GetProperty("events");
        var decisionUtc = ParseUtc(intent.GetProperty("created_at").GetString()!);

        JsonElement sourceEvent = default;
        DateTime? sourceEventUtc = null;
        foreach (var candidate in events.EnumerateArray())
        {
            if (candidate.GetProperty("instrument_id").GetString() != intent.GetProperty("instrument_id").GetString())
            {
                continue;
            }
            var eventUtc = ParseUtc(candidate.GetProperty("event_time").GetString()!);
            if (eventUtc <= decisionUtc)
            {
                continue;
            }
            if (sourceEventUtc is null || eventUtc < sourceEventUtc.Value)
            {
                sourceEvent = candidate;
                sourceEventUtc = eventUtc;
            }
        }
        if (sourceEventUtc is null)
        {
            throw new InvalidOperationException("fixture lacks a next eligible event after the decision boundary");
        }

        var payload = sourceEvent.GetProperty("payload");
        var instrument = intent.GetProperty("instrument_id").GetString()!;
        var side = intent.GetProperty("side").GetString()!;
        var quantity = decimal.Parse(intent.GetProperty("quantity").GetString()!, CultureInfo.InvariantCulture);
        if (side.Equals("SELL", StringComparison.OrdinalIgnoreCase))
        {
            quantity = -quantity;
        }
        else if (!side.Equals("BUY", StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException($"unsupported side: {side}");
        }

        var open = decimal.Parse(payload.GetProperty("open").GetString()!, CultureInfo.InvariantCulture);
        var high = decimal.Parse(payload.GetProperty("high").GetString()!, CultureInfo.InvariantCulture);
        var low = decimal.Parse(payload.GetProperty("low").GetString()!, CultureInfo.InvariantCulture);
        var close = decimal.Parse(payload.GetProperty("close").GetString()!, CultureInfo.InvariantCulture);

        var exchangeHours = CreateWeekdayHours();
        var sid = SecurityIdentifier.GenerateEquity(instrument, Market.USA, mapSymbol: false);
        var symbol = new Symbol(sid, instrument);
        var config = new SubscriptionDataConfig(
            typeof(TradeBar),
            symbol,
            Resolution.Daily,
            TimeZones.NewYork,
            TimeZones.NewYork,
            fillForward: true,
            extendedHours: false,
            isInternalFeed: false,
            dataNormalizationMode: DataNormalizationMode.Raw);
        var equity = new Equity(
            exchangeHours,
            config,
            new Cash(Currencies.USD, 0m, 1m),
            SymbolProperties.GetDefault(Currencies.USD),
            ErrorCurrencyConverter.Instance,
            RegisteredSecurityDataTypesProvider.Null,
            Exchange.ARCA);

        // Order.Time is UTC. Derive the market boundary from the fixture intent instead
        // of hard-coding the A1 fixture date so A2 can reuse this exact production probe.
        var decisionLocal = decisionUtc.ConvertFromUtc(TimeZones.NewYork);
        var timeKeeper = new TimeKeeper(decisionUtc, TimeZones.NewYork);
        equity.SetLocalTimeKeeper(timeKeeper.GetLocalTimeKeeper(TimeZones.NewYork));

        var order = new MarketOnOpenOrder(symbol, quantity, decisionUtc);
        var nextOpen = exchangeHours.GetNextMarketOpen(decisionLocal, false);
        timeKeeper.SetUtcDateTime(nextOpen.ConvertToUtc(TimeZones.NewYork));

        var bar = new TradeBar(nextOpen.RoundDown(Time.OneDay), symbol, open, high, low, close, 100m, Time.OneDay);
        equity.SetMarketPrice(bar);

        var model = (EquityFillModel)equity.FillModel;
        var fill = model.Fill(new FillModelParameters(
            equity,
            order,
            new SingleConfigProvider(config),
            Time.OneHour,
            null)).Single();

        var result = new
        {
            engine = "LEAN",
            probe_scope = "EquityFillModel.MarketOnOpenFill",
            order_type = "MarketOnOpen",
            status = fill.Status.ToString(),
            fill_quantity = fill.FillQuantity.ToString(CultureInfo.InvariantCulture),
            fill_price = fill.FillPrice.ToString(CultureInfo.InvariantCulture),
            fill_time = fill.UtcTime.ToUniversalTime().ToString("O"),
            source_event_id = sourceEvent.GetProperty("event_id").GetString(),
            instrument_id = instrument,
            fill_message = fill.Message
        };
        Console.WriteLine(JsonSerializer.Serialize(result));
        return fill.Status == OrderStatus.Filled ? 0 : 3;
    }
}
