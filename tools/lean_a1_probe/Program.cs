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

    public static int Main(string[] args)
    {
        if (args.Length != 1)
        {
            Console.Error.WriteLine("usage: LeanA1Probe <fixture.json>");
            return 2;
        }

        using var document = JsonDocument.Parse(File.ReadAllText(args[0]));
        var root = document.RootElement;
        var intent = root.GetProperty("intents")[0];
        var events = root.GetProperty("events");
        var sourceEvent = events[1];
        var payload = sourceEvent.GetProperty("payload");

        var instrument = intent.GetProperty("instrument_id").GetString()!;
        var side = intent.GetProperty("side").GetString()!;
        var quantity = decimal.Parse(intent.GetProperty("quantity").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
        if (side.Equals("SELL", StringComparison.OrdinalIgnoreCase))
        {
            quantity = -quantity;
        }
        else if (!side.Equals("BUY", StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException($"unsupported side: {side}");
        }

        var open = decimal.Parse(payload.GetProperty("open").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
        var high = decimal.Parse(payload.GetProperty("high").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
        var low = decimal.Parse(payload.GetProperty("low").GetString()!, System.Globalization.CultureInfo.InvariantCulture);
        var close = decimal.Parse(payload.GetProperty("close").GetString()!, System.Globalization.CultureInfo.InvariantCulture);

        var exchangeHours = CreateWeekdayHours();
        var symbol = Symbol.Create(instrument, SecurityType.Equity, Market.USA);
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

        // The public fixture's decision boundary is the first bar close: 16:00 New York.
        // LEAN Order.Time is UTC. Mirror the pinned upstream EquityFillModel tests rather
        // than passing a local wall-clock DateTime through a UTC-valued contract.
        var decisionLocal = new DateTime(2026, 6, 1, 16, 0, 0, DateTimeKind.Unspecified);
        var decisionUtc = decisionLocal.ConvertToUtc(TimeZones.NewYork);
        var timeKeeper = new TimeKeeper(decisionUtc, TimeZones.NewYork);
        equity.SetLocalTimeKeeper(timeKeeper.GetLocalTimeKeeper(TimeZones.NewYork));

        var order = new MarketOnOpenOrder(symbol, quantity, decisionUtc);
        var nextOpen = exchangeHours.GetNextMarketOpen(decisionLocal, false);
        timeKeeper.SetUtcDateTime(nextOpen.ConvertToUtc(TimeZones.NewYork));

        // LEAN's own regression suite exercises daily MarketOnOpen fills by updating the
        // security with the completed daily TradeBar and then invoking EquityFillModel.
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
            fill_quantity = fill.FillQuantity.ToString(System.Globalization.CultureInfo.InvariantCulture),
            fill_price = fill.FillPrice.ToString(System.Globalization.CultureInfo.InvariantCulture),
            fill_time = fill.UtcTime.ToUniversalTime().ToString("O"),
            source_event_id = sourceEvent.GetProperty("event_id").GetString(),
            instrument_id = instrument,
            fill_message = fill.Message
        };
        Console.WriteLine(JsonSerializer.Serialize(result));
        return fill.Status == OrderStatus.Filled ? 0 : 3;
    }
}
