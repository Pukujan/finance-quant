"""Evaluate a PIT-safe pre-open native latency/timer path in pinned NautilusTrader.

The MARKET intent is submitted from the decision-bar callback with a non-zero native
insert latency. A native strategy clock alert, whose timestamp is supplied from the
session/calendar contract rather than future bar payload, creates a settlement point
strictly before the next session open. Production SimulatedExchange matching remains
unchanged; this probe does not install a custom fill model.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import LoggingConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos, unix_nanos_to_dt
from nautilus_trader.data.config import DataEngineConfig
from nautilus_trader.execution import StaticLatencyModel
from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType, OrderSide, TimeInForce
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.objects import Money, Quantity
from nautilus_trader.trading.strategy import Strategy

from tools.nautilus_a1_probe.probe import VENUE, _instant, _instrument


def _iso_from_nanos(value: int) -> str:
    return unix_nanos_to_dt(value).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class PreOpenProbeStrategy(Strategy):
    def __init__(self, bar_type: BarType, intent: dict[str, object], release_time: datetime):
        super().__init__()
        self.bar_type = bar_type
        self.intent = intent
        self.release_time = release_time
        self.bar_count = 0
        self.fill_events: list[object] = []
        self.release_fired = False
        self.release_observed_ns: int | None = None

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
        self.clock.set_time_alert("fq-preopen-release", self.release_time, self._on_release)

    def _on_release(self, event: object) -> None:
        self.release_fired = True
        self.release_observed_ns = int(self.clock.timestamp_ns())

    def on_order_filled(self, event: object) -> None:
        self.fill_events.append(event)


def run(fixture: dict[str, object], *, release_time: datetime) -> dict[str, object]:
    events = list(fixture.get("events", []))
    intents = list(fixture.get("intents", []))
    if len(events) != 2 or len(intents) != 1:
        raise ValueError("pre-open Nautilus probe requires exactly two bars and one intent")
    intent = dict(intents[0])
    if str(intent["order_type"]).upper() != "MARKET":
        raise ValueError("pre-open Nautilus probe requires a MARKET intent")

    symbol = str(intent["instrument_id"])
    instrument = _instrument(symbol)
    bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
    bars: list[Bar] = []
    event_by_ns: dict[int, str] = {}
    for raw in events:
        event = dict(raw)
        if str(event["instrument_id"]) != symbol:
            raise ValueError("all probe bars must match the intent instrument")
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

    release_ns = int(dt_to_unix_nanos(release_time))
    decision_ns = int(bars[0].ts_init)
    next_bar_ns = int(bars[1].ts_init)
    if not (decision_ns < release_ns < next_bar_ns):
        raise ValueError("release time must be strictly after the decision bar and before the next bar")

    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id=TraderId("FQ-A1-002"),
            data_engine=DataEngineConfig(validate_data_sequence=True),
            logging=LoggingConfig(log_level="ERROR"),
        )
    )
    engine.add_venue(
        venue=VENUE,
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        starting_balances=[Money(float(str(fixture["initial_cash"])), USDT)],
        base_currency=None,
        default_leverage=Decimal("1"),
        latency_model=StaticLatencyModel(insert_latency_nanos=1),
    )
    engine.add_instrument(instrument)
    engine.add_data(bars)
    strategy = PreOpenProbeStrategy(bar_type=bar_type, intent=intent, release_time=release_time)
    engine.add_strategy(strategy)
    try:
        engine.run()
        fills = strategy.fill_events
        result: dict[str, object] = {
            "engine": "NautilusTrader",
            "probe_scope": "BacktestEngine.SimulatedExchange.native-latency-clock-settlement",
            "time_in_force": "GTC",
            "submission_policy": "DECISION_BAR_CALLBACK_WITH_NATIVE_1NS_INSERT_LATENCY",
            "release_policy": "SESSION_CONTRACT_PREOPEN_CLOCK_ALERT",
            "release_time": _iso_from_nanos(release_ns),
            "release_fired": strategy.release_fired,
            "release_observed_time": (
                _iso_from_nanos(strategy.release_observed_ns)
                if strategy.release_observed_ns is not None
                else None
            ),
            "custom_fill_model": False,
            "instrument_id": symbol,
        }
        if len(fills) != 1:
            result.update(
                status="UNFILLED" if not fills else "AMBIGUOUS_MULTIFILL",
                fill_count=len(fills),
            )
            return result
        fill = fills[0]
        ts_event = int(getattr(fill, "ts_event"))
        side = str(intent["side"]).upper()
        quantity = Decimal(str(getattr(fill, "last_qty")))
        signed_quantity = quantity if side == "BUY" else -quantity
        result.update(
            status="FILLED",
            fill_quantity=str(signed_quantity),
            fill_price=str(getattr(fill, "last_px")),
            fill_time=_iso_from_nanos(ts_event),
            source_event_id=event_by_ns.get(ts_event, "NON_BAR_TIMER_OR_UNKNOWN"),
        )
        return result
    finally:
        engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--release-time", required=True)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    release_time = _instant(args.release_time)
    print(json.dumps(run(fixture, release_time=release_time), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
