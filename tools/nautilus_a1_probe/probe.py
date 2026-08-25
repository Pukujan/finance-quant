"""Credential-free A1 probe of pinned NautilusTrader production bar matching."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import LoggingConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos, unix_nanos_to_dt
from nautilus_trader.data.config import DataEngineConfig
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.currencies import ADA, USDT
from nautilus_trader.model.enums import AccountType, OmsType, OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId, Symbol, TraderId, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.trading.strategy import Strategy


VENUE = Venue("FQSIM")


def _instant(value: str) -> datetime:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    result = datetime.fromisoformat(text)
    if result.tzinfo is None:
        raise ValueError(f"timestamp must be offset-aware: {value}")
    return result.astimezone(timezone.utc)


def _iso_from_nanos(value: int) -> str:
    return unix_nanos_to_dt(value).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _instrument(symbol: str) -> CurrencyPair:
    return CurrencyPair(
        instrument_id=InstrumentId(symbol=Symbol(symbol), venue=VENUE),
        raw_symbol=Symbol(symbol),
        base_currency=ADA,
        quote_currency=USDT,
        price_precision=2,
        size_precision=0,
        price_increment=Price.from_str("0.01"),
        size_increment=Quantity.from_int(1),
        lot_size=None,
        max_quantity=Quantity.from_int(1_000_000),
        min_quantity=Quantity.from_int(1),
        max_notional=None,
        min_notional=None,
        max_price=Price.from_str("1000000.00"),
        min_price=Price.from_str("0.01"),
        margin_init=Decimal("0"),
        margin_maint=Decimal("0"),
        maker_fee=Decimal("0"),
        taker_fee=Decimal("0"),
        ts_event=0,
        ts_init=0,
    )


class ProbeStrategy(Strategy):
    def __init__(self, bar_type: BarType, intent: dict[str, object]):
        super().__init__()
        self.bar_type = bar_type
        self.intent = intent
        self.bar_count = 0
        self.fill_events: list[object] = []

    def on_start(self) -> None:
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar: Bar) -> None:
        self.bar_count += 1
        if self.bar_count != 1:
            return
        side = str(self.intent["side"]).upper()
        order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
        order = self.order_factory.market(
            instrument_id=self.bar_type.instrument_id,
            order_side=order_side,
            quantity=Quantity.from_str(str(self.intent["quantity"])),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def on_order_filled(self, event: object) -> None:
        self.fill_events.append(event)


def run(fixture: dict[str, object]) -> dict[str, object]:
    events = list(fixture.get("events", []))
    intents = list(fixture.get("intents", []))
    if len(events) != 2 or len(intents) != 1:
        raise ValueError("initial Nautilus production probe requires exactly two bars and one intent")
    intent = dict(intents[0])
    symbol = str(intent["instrument_id"])
    if any(str(dict(item)["instrument_id"]) != symbol for item in events):
        raise ValueError("all probe bars must match the intent instrument")
    if str(intent["order_type"]).upper() != "MARKET":
        raise ValueError("initial Nautilus production probe requires a MARKET intent")

    instrument = _instrument(symbol)
    bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
    bars: list[Bar] = []
    event_by_ns: dict[int, str] = {}
    for raw in events:
        event = dict(raw)
        payload = dict(event["payload"])
        ts = dt_to_unix_nanos(_instant(str(event["event_time"])))
        event_by_ns[int(ts)] = str(event["event_id"])
        bars.append(
            Bar(
                bar_type=bar_type,
                open=instrument.make_price(float(str(payload["open"]))),
                high=instrument.make_price(float(str(payload["high"]))),
                low=instrument.make_price(float(str(payload["low"]))),
                close=instrument.make_price(float(str(payload["close"]))),
                volume=Quantity.from_str(str(payload["liquidity"])),
                ts_event=ts,
                ts_init=ts,
            )
        )

    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id=TraderId("FQ-A1-001"),
            data_engine=DataEngineConfig(validate_data_sequence=True),
            logging=LoggingConfig(log_level="ERROR"),
        )
    )
    engine.add_venue(
        venue=VENUE,
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        starting_balances=[Money(float(str(fixture["initial_cash"])), USDT)],
        base_currency=USDT,
        default_leverage=Decimal("1"),
    )
    engine.add_instrument(instrument)
    engine.add_data(bars)
    strategy = ProbeStrategy(bar_type=bar_type, intent=intent)
    engine.add_strategy(strategy)
    try:
        engine.run()
        fills = strategy.fill_events
        if len(fills) != 1:
            return {
                "engine": "NautilusTrader",
                "probe_scope": "BacktestEngine.SimulatedExchange.process_bar",
                "status": "UNFILLED" if not fills else "AMBIGUOUS_MULTIFILL",
                "fill_count": len(fills),
                "instrument_id": symbol,
            }
        fill = fills[0]
        ts_event = int(getattr(fill, "ts_event"))
        side = str(intent["side"]).upper()
        quantity = Decimal(str(getattr(fill, "last_qty")))
        signed_quantity = quantity if side == "BUY" else -quantity
        return {
            "engine": "NautilusTrader",
            "probe_scope": "BacktestEngine.SimulatedExchange.process_bar",
            "status": "FILLED",
            "instrument_id": symbol,
            "fill_quantity": str(signed_quantity),
            "fill_price": str(getattr(fill, "last_px")),
            "fill_time": _iso_from_nanos(ts_event),
            "source_event_id": event_by_ns.get(ts_event, "UNKNOWN"),
        }
    finally:
        engine.dispose()


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: probe.py FIXTURE.json")
    fixture = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(run(fixture), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
