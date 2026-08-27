"""Deliberately boring PIT-safe A2 baseline strategy."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

D = Decimal
A2_BASELINE_STRATEGY_ID = "a2-two-close-trend-v1"


class StrategyInvariantError(ValueError):
    pass


def _hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise StrategyInvariantError(f"{field} must be a decimal") from exc
    if not result.is_finite():
        raise StrategyInvariantError(f"{field} must be finite")
    return result


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _time(value: object, *, field: str) -> datetime:
    text = str(value)
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StrategyInvariantError(f"{field} must be ISO-8601") from exc
    if result.tzinfo is None:
        raise StrategyInvariantError(f"{field} must include timezone")
    return result


@dataclass(frozen=True)
class BaselineStrategyConfig:
    quantity: str = "1"
    risk_notional: str = "0.1"

    def normalized(self) -> dict[str, str]:
        quantity = _decimal(self.quantity, field="quantity")
        risk_notional = _decimal(self.risk_notional, field="risk_notional")
        if quantity <= 0:
            raise StrategyInvariantError("quantity must be positive")
        if risk_notional < 0:
            raise StrategyInvariantError("risk_notional must be non-negative")
        return {"quantity": _text(quantity), "risk_notional": _text(risk_notional)}


@dataclass(frozen=True)
class PortfolioIntent:
    intent_id: str
    instrument_id: str
    created_at: str
    side: str
    quantity: str
    risk_notional: str
    order_type: str = "MARKET"

    def execution_intent(self) -> dict[str, str]:
        return {
            "intent_id": self.intent_id,
            "instrument_id": self.instrument_id,
            "created_at": self.created_at,
            "side": self.side,
            "quantity": self.quantity,
            "order_type": self.order_type,
        }


@dataclass(frozen=True)
class StrategyDecision:
    strategy_id: str
    strategy_spec_hash: str
    strategy_hash: str
    status: str
    session_id: str
    instrument_id: str
    decision_time: str
    source_event_ids: tuple[str, ...]
    intent: PortfolioIntent | None


def _ordered_unique_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event.get("event_id", ""))
        if not event_id:
            raise StrategyInvariantError("event_id must be non-empty")
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise StrategyInvariantError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(
        seen.values(),
        key=lambda event: (
            _time(event["event_time"], field="event_time"),
            int(event["sequence"]),
            str(event["event_id"]),
        ),
    )


def baseline_strategy_spec_hash(config: BaselineStrategyConfig = BaselineStrategyConfig()) -> str:
    return _hash({"strategy_id": A2_BASELINE_STRATEGY_ID, **config.normalized()})


def generate_baseline_decision(
    events: list[Mapping[str, Any]],
    *,
    session_id: str,
    instrument_id: str,
    decision_time: str,
    config: BaselineStrategyConfig = BaselineStrategyConfig(),
) -> StrategyDecision:
    """Generate a two-close trend intent using only information knowable at decision_time.

    Up close -> BUY, down close -> SELL, flat/insufficient history -> NO_INTENT.
    This is intentionally not an alpha claim; it is deterministic A2 plumbing evidence.
    """
    if not session_id or not instrument_id:
        raise StrategyInvariantError("session_id and instrument_id must be non-empty")
    decision_dt = _time(decision_time, field="decision_time")
    normalized_config = config.normalized()
    spec_hash = baseline_strategy_spec_hash(config)
    ordered = _ordered_unique_events(events)
    available: list[dict[str, Any]] = []
    for event in ordered:
        if str(event.get("instrument_id", "")) != instrument_id:
            continue
        event_time = _time(event["event_time"], field="event_time")
        known_at = _time(event["known_at"], field="known_at")
        if event_time <= decision_dt and known_at <= decision_dt:
            payload = event.get("payload")
            if not isinstance(payload, Mapping) or "close" not in payload:
                raise StrategyInvariantError("available bar must contain payload.close")
            _decimal(payload["close"], field="payload.close")
            available.append(event)

    used = available[-2:]
    intent: PortfolioIntent | None = None
    status = "NO_INTENT"
    if len(used) == 2:
        previous_close = _decimal(used[0]["payload"]["close"], field="previous.close")
        current_close = _decimal(used[1]["payload"]["close"], field="current.close")
        if current_close != previous_close:
            side = "BUY" if current_close > previous_close else "SELL"
            intent_seed = {
                "strategy_id": A2_BASELINE_STRATEGY_ID,
                "session_id": session_id,
                "instrument_id": instrument_id,
                "decision_time": decision_time,
                "side": side,
                "quantity": normalized_config["quantity"],
                "source_event_ids": [str(item["event_id"]) for item in used],
            }
            intent = PortfolioIntent(
                intent_id=f"intent:{_hash(intent_seed)[:32]}",
                instrument_id=instrument_id,
                created_at=decision_time,
                side=side,
                quantity=normalized_config["quantity"],
                risk_notional=normalized_config["risk_notional"],
            )
            status = "INTENT"

    evidence = {
        "strategy_id": A2_BASELINE_STRATEGY_ID,
        "strategy_spec_hash": spec_hash,
        "status": status,
        "session_id": session_id,
        "instrument_id": instrument_id,
        "decision_time": decision_time,
        "used_events": used,
        "intent": None if intent is None else asdict(intent),
    }
    return StrategyDecision(
        strategy_id=A2_BASELINE_STRATEGY_ID,
        strategy_spec_hash=spec_hash,
        strategy_hash=_hash(evidence),
        status=status,
        session_id=session_id,
        instrument_id=instrument_id,
        decision_time=decision_time,
        source_event_ids=tuple(str(item["event_id"]) for item in used),
        intent=intent,
    )
