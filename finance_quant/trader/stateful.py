"""Stateful A2 session planning and account-aware execution rebasing."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from finance_quant.execution.conformance import canonical_receipt_hash, load_runtime_contract, validate_receipt
from finance_quant.risk.veto import PortfolioState, RiskLimits

from .account import VirtualAccountStore
from .risk import gate_portfolio_intent
from .strategy import BaselineStrategyConfig, generate_baseline_decision

D = Decimal


class StatefulSessionError(ValueError):
    pass


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise StatefulSessionError(f"{field} must be decimal") from exc
    if not result.is_finite():
        raise StatefulSessionError(f"{field} must be finite")
    return result


def _text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _time(value: object) -> datetime:
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise StatefulSessionError("timestamps must be timezone-aware")
    return result


def _canonical_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event.get("event_id", ""))
        if not event_id:
            raise StatefulSessionError("event_id must be non-empty")
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise StatefulSessionError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(seen.values(), key=lambda event: (_time(event["event_time"]), int(event["sequence"]), event_id if (event_id := str(event["event_id"])) else ""))


def _marks_at(events: list[Mapping[str, Any]], decision_time: str, instruments: set[str]) -> dict[str, str]:
    cutoff = _time(decision_time)
    marks: dict[str, str] = {}
    for event in _canonical_events(events):
        instrument = str(event.get("instrument_id", ""))
        if instrument not in instruments:
            continue
        if _time(event["event_time"]) <= cutoff and _time(event["known_at"]) <= cutoff:
            payload = event.get("payload")
            if not isinstance(payload, Mapping) or "close" not in payload:
                raise StatefulSessionError("PIT-safe mark event must contain payload.close")
            marks[instrument] = _text(_decimal(payload["close"], field=f"mark[{instrument}]"))
    missing = instruments - set(marks)
    if missing:
        raise StatefulSessionError(f"missing PIT-safe marks for open positions: {sorted(missing)}")
    return marks


def account_portfolio_state(
    store: VirtualAccountStore,
    events: list[Mapping[str, Any]],
    decision_time: str,
    *,
    loss: float = 0.0,
) -> tuple[PortfolioState, dict[str, str]]:
    state = store.authoritative_state()
    positions = {
        str(item["instrument_id"]): _decimal(item["quantity"], field="position.quantity")
        for item in state["positions"]
        if _decimal(item["quantity"], field="position.quantity") != 0
    }
    if not positions:
        return PortfolioState(gross_exposure=0.0, net_exposure=0.0, loss=float(loss)), {}
    marks = _marks_at(events, decision_time, set(positions))
    nav = _decimal(store.nav(marks)["nav"], field="nav")
    if nav <= 0:
        raise StatefulSessionError("risk normalization requires positive NAV")
    gross_value = sum((abs(quantity * _decimal(marks[symbol], field="mark")) for symbol, quantity in positions.items()), D("0"))
    net_value = sum((quantity * _decimal(marks[symbol], field="mark") for symbol, quantity in positions.items()), D("0"))
    return PortfolioState(
        gross_exposure=float(gross_value / nav),
        net_exposure=float(net_value / nav),
        loss=float(loss),
    ), marks


def plan_stateful_session(store: VirtualAccountStore, spec: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    events = _canonical_events(list(spec.get("events", [])))
    config = BaselineStrategyConfig(**dict(spec.get("strategy_config", {})))
    decision = generate_baseline_decision(
        events,
        session_id=str(spec["session_id"]),
        instrument_id=str(spec["instrument_id"]),
        decision_time=str(spec["decision_time"]),
        config=config,
    )
    if decision.status != "INTENT" or decision.intent is None:
        raise StatefulSessionError("controlled stateful session must produce one intent")
    risk_state, marks = account_portfolio_state(
        store,
        events,
        str(spec["decision_time"]),
        loss=float(spec.get("loss", 0.0)),
    )
    limits = RiskLimits(**dict(spec.get("risk_limits", {})))
    gated = gate_portfolio_intent(risk_state, decision.intent, limits)
    if gated.decision.status != "APPROVED" or gated.approved_intent is None:
        raise StatefulSessionError(f"mechanical risk gate rejected controlled session: {gated.decision.reason}")
    current = store.authoritative_state()
    fixture = {
        "fixture_id": str(spec["fixture_id"]),
        "initial_cash": str(current["cash"]),
        "fee_per_unit": str(spec.get("fee_per_unit", "0")),
        "events": events,
        "intents": [gated.approved_intent.execution_intent()],
    }
    evidence = {
        "schema_version": "1.0.0",
        "issue": 16,
        "phase": "A2",
        "session_id": str(spec["session_id"]),
        "prior_account_state_hash": store.state_hash(),
        "risk_state": asdict(risk_state),
        "risk_marks": marks,
        "strategy_id": decision.strategy_id,
        "strategy_spec_hash": decision.strategy_spec_hash,
        "strategy_hash": decision.strategy_hash,
        "strategy_source_event_ids": list(decision.source_event_ids),
        "risk_hash": gated.risk_hash,
        "risk_decision": asdict(gated.decision),
        "authority": "NONE",
    }
    return fixture, evidence


def rebase_incremental_execution(
    store: VirtualAccountStore,
    receipt: Mapping[str, Any],
    fixture: Mapping[str, Any],
) -> dict[str, Any]:
    """Rebase a fully A1-conformant incremental LEAN receipt onto durable A2 account state."""
    contract = load_runtime_contract()
    validate_receipt(receipt, contract)
    if receipt.get("receipt_hash") != canonical_receipt_hash(receipt, contract):
        raise StatefulSessionError("incremental execution receipt hash mismatch")
    if receipt.get("runtime") != "lean" or receipt.get("status") != "COMPLETE":
        raise StatefulSessionError("stateful rebasing requires a complete normalized LEAN receipt")

    intents = {str(item["intent_id"]): dict(item) for item in fixture.get("intents", [])}
    deltas: dict[str, Decimal] = {}
    for fill in receipt.get("fills", []):
        intent = intents.get(str(fill["intent_id"]))
        if intent is None:
            raise StatefulSessionError("fill references unknown intent")
        side = str(intent["side"]).upper()
        quantity = _decimal(fill["quantity"], field="fill.quantity")
        signed = quantity if side == "BUY" else -quantity if side == "SELL" else None
        if signed is None:
            raise StatefulSessionError("unsupported intent side")
        instrument = str(fill["instrument_id"])
        deltas[instrument] = deltas.get(instrument, D("0")) + signed

    incremental_positions = {
        str(item["instrument_id"]): _decimal(item["quantity"], field="receipt.position")
        for item in receipt.get("positions", [])
        if _decimal(item["quantity"], field="receipt.position") != 0
    }
    if incremental_positions != {key: value for key, value in deltas.items() if value != 0}:
        raise StatefulSessionError("incremental receipt positions do not equal fill deltas")

    prior = store.authoritative_state()
    prior_cash = _decimal(prior["cash"], field="prior.cash")
    cash_delta = sum((_decimal(item["amount"], field="cash_ledger.amount") for item in receipt.get("cash_ledger", [])), D("0"))
    terminal_cash = prior_cash + cash_delta
    if _decimal(receipt["cash"], field="receipt.cash") != terminal_cash:
        raise StatefulSessionError("incremental receipt cash is not based on durable prior cash")

    positions: dict[str, Decimal] = {
        str(item["instrument_id"]): _decimal(item["quantity"], field="prior.position")
        for item in prior["positions"]
    }
    for instrument, delta in deltas.items():
        positions[instrument] = positions.get(instrument, D("0")) + delta
    positions = {key: value for key, value in positions.items() if value != 0}

    marks: dict[str, Decimal] = {}
    for event in _canonical_events(list(fixture.get("events", []))):
        if _time(event["known_at"]) <= _time(event["event_time"]):
            payload = event.get("payload", {})
            if "close" in payload:
                marks[str(event["instrument_id"])] = _decimal(payload["close"], field="terminal.mark")
    missing = set(positions) - set(marks)
    if missing:
        raise StatefulSessionError(f"missing terminal marks for positions: {sorted(missing)}")
    equity = sum((quantity * marks[instrument] for instrument, quantity in positions.items()), D("0"))
    nav = terminal_cash + equity

    rebased = deepcopy(dict(receipt))
    rebased["cash"] = _text(terminal_cash)
    rebased["positions"] = [
        {"instrument_id": instrument, "quantity": _text(quantity)}
        for instrument, quantity in sorted(positions.items())
    ]
    rebased["equity"] = _text(equity)
    rebased["nav"] = _text(nav)
    rebased["receipt_hash"] = ""
    rebased["receipt_hash"] = canonical_receipt_hash(rebased, contract)
    return rebased
