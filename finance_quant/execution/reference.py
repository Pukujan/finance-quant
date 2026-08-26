"""Tiny independent A1 execution oracle for the shared daily-bar subset.

This is deliberately not a production trading engine. It exists only to falsify
candidate adapter behavior against finance-quant-owned semantics.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any, Mapping

from .conformance import canonical_receipt_hash, validate_receipt

D = Decimal


class ReferenceExecutionError(ValueError):
    pass


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _ordered_unique_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event["event_id"])
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise ReferenceExecutionError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(seen.values(), key=lambda e: (e["event_time"], int(e["sequence"]), e["event_id"]))


def run_daily_reference(fixture: Mapping[str, Any], contract: Mapping[str, Any], *, seed: int = 0) -> dict[str, Any]:
    """Execute a minimal deterministic market-order daily-bar fixture.

    Supported subset: BUY/SELL market intents, deterministic per-unit fees, next-event
    fills, and event-declared liquidity. Partial fills are allowed. Events whose
    ``known_at`` is after their own event_time are unavailable for execution.
    """
    events = _ordered_unique_events(list(fixture.get("events", [])))
    intents = sorted(
        (dict(item) for item in fixture.get("intents", [])),
        key=lambda i: (i["created_at"], i["intent_id"]),
    )
    normalized_input = dict(fixture)
    normalized_input["events"] = events
    normalized_input["intents"] = intents

    initial_cash = D(str(fixture.get("initial_cash", "0")))
    cash = initial_cash
    positions: dict[str, D] = {}
    orders: list[dict[str, Any]] = []
    fills: list[dict[str, Any]] = []
    cash_ledger: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    fee_per_unit = D(str(fixture.get("fee_per_unit", "0")))

    for intent in intents:
        qty = D(str(intent["quantity"]))
        if qty <= 0:
            raise ReferenceExecutionError("intent quantity must be positive")
        side = str(intent["side"]).upper()
        if side not in {"BUY", "SELL"}:
            raise ReferenceExecutionError(f"unsupported side: {side}")
        instrument = str(intent["instrument_id"])
        eligible = [
            event for event in events
            if event["instrument_id"] == instrument
            and event["event_time"] > intent["created_at"]
            and event["known_at"] <= event["event_time"]
            and D(str(event.get("payload", {}).get("liquidity", "0"))) > 0
        ]
        order_id = f"order:{intent['intent_id']}"
        if not eligible:
            orders.append({"order_id": order_id, "intent_id": intent["intent_id"], "state": "REJECTED", "quantity": str(qty)})
            rejections.append({"intent_id": intent["intent_id"], "reason": "NO_ELIGIBLE_LIQUIDITY"})
            continue

        event = eligible[0]
        available = D(str(event["payload"]["liquidity"]))
        fill_qty = min(qty, available)
        price = D(str(event["payload"]["open"]))
        fee = fill_qty * fee_per_unit
        signed_qty = fill_qty if side == "BUY" else -fill_qty
        cash_delta = -(fill_qty * price) - fee if side == "BUY" else (fill_qty * price) - fee
        cash += cash_delta
        positions[instrument] = positions.get(instrument, D("0")) + signed_qty
        state = "FILLED" if fill_qty == qty else "PARTIALLY_FILLED"
        orders.append({"order_id": order_id, "intent_id": intent["intent_id"], "state": state, "quantity": str(qty), "filled_quantity": str(fill_qty)})
        fill_id = f"fill:{intent['intent_id']}:{event['event_id']}"
        fills.append({
            "fill_id": fill_id,
            "order_id": order_id,
            "intent_id": intent["intent_id"],
            "instrument_id": instrument,
            "event_time": event["event_time"],
            "quantity": str(fill_qty),
            "price": str(price),
            "fee": str(fee),
            "slippage": "0",
            "source_event_id": event["event_id"],
        })
        cash_ledger.append({"entry_id": f"cash:{fill_id}", "kind": "FILL", "amount": str(cash_delta)})

    last_mark: dict[str, D] = {}
    for event in events:
        if event["known_at"] <= event["event_time"]:
            last_mark[str(event["instrument_id"])] = D(str(event.get("payload", {}).get("close", event.get("payload", {}).get("open", "0"))))
    equity = sum((qty * last_mark.get(symbol, D("0")) for symbol, qty in positions.items()), D("0"))
    nav = cash + equity
    receipt: dict[str, Any] = {
        "contract_version": contract["schema_version"],
        "fixture_id": fixture["fixture_id"],
        "runtime": "finance-quant-reference",
        "runtime_version": "a1-v0",
        "seed": seed,
        "status": "COMPLETE",
        "orders": orders,
        "fills": fills,
        "cash_ledger": cash_ledger,
        "positions": [{"instrument_id": symbol, "quantity": str(qty)} for symbol, qty in sorted(positions.items())],
        "corporate_actions": [],
        "rejections": rejections,
        "faults": [],
        "cash": str(cash),
        "equity": str(equity),
        "nav": str(nav),
        "realized_pnl": "0",
        "unrealized_pnl": str(nav - initial_cash),
        "input_hash": _canonical_hash(normalized_input),
        "receipt_hash": "",
        "replay_lineage": {"parent_receipt_hash": None, "committed_event_count": len(events)},
    }
    validate_receipt(receipt, contract)
    receipt["receipt_hash"] = canonical_receipt_hash(receipt, contract)
    return receipt


def restart_daily_reference_from_checkpoint(
    fixture: Mapping[str, Any],
    contract: Mapping[str, Any],
    checkpoint_receipt: Mapping[str, Any],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    """Validate a committed checkpoint and deterministically replay to final state.

    The reference oracle deliberately favors a simple, fail-closed replay model over a
    mutable resume implementation. A restart accepts a checkpoint only when its hash,
    identity, seed, committed boundary, and complete normalized state exactly match the
    deterministic prefix implied by the immutable fixture. The full fixture is then
    replayed and linked to the validated checkpoint. This gives A1 an executable
    restart/convergence oracle without granting production execution authority.
    """
    validate_receipt(checkpoint_receipt, contract)
    checkpoint = dict(checkpoint_receipt)
    expected_hash = canonical_receipt_hash(checkpoint, contract)
    if checkpoint.get("receipt_hash") != expected_hash:
        raise ReferenceExecutionError("checkpoint receipt_hash mismatch")
    if checkpoint.get("runtime") != "finance-quant-reference" or checkpoint.get("runtime_version") != "a1-v0":
        raise ReferenceExecutionError("checkpoint runtime identity mismatch")
    if checkpoint.get("fixture_id") != fixture.get("fixture_id"):
        raise ReferenceExecutionError("checkpoint fixture identity mismatch")
    if checkpoint.get("seed") != seed:
        raise ReferenceExecutionError("checkpoint seed mismatch")

    lineage = checkpoint.get("replay_lineage")
    if not isinstance(lineage, Mapping):
        raise ReferenceExecutionError("checkpoint replay_lineage is invalid")
    boundary = lineage.get("committed_event_count")
    if type(boundary) is not int or boundary < 0:
        raise ReferenceExecutionError("checkpoint committed_event_count is invalid")

    events = _ordered_unique_events(list(fixture.get("events", [])))
    if boundary > len(events):
        raise ReferenceExecutionError("checkpoint committed_event_count exceeds fixture")

    prefix_fixture = dict(fixture)
    prefix_fixture["events"] = events[:boundary]
    if boundary == 0:
        prefix_fixture["intents"] = []
    else:
        boundary_time = events[boundary - 1]["event_time"]
        prefix_fixture["intents"] = [
            dict(intent)
            for intent in fixture.get("intents", [])
            if intent["created_at"] <= boundary_time
        ]
    expected_checkpoint = run_daily_reference(prefix_fixture, contract, seed=seed)
    if checkpoint != expected_checkpoint:
        raise ReferenceExecutionError("checkpoint does not match committed fixture boundary")

    resumed = run_daily_reference(fixture, contract, seed=seed)
    resumed["replay_lineage"] = {
        "parent_receipt_hash": checkpoint["receipt_hash"],
        "committed_event_count": len(events),
    }
    resumed["receipt_hash"] = ""
    validate_receipt(resumed, contract)
    resumed["receipt_hash"] = canonical_receipt_hash(resumed, contract)
    return resumed
