"""Thin A1 LEAN candidate adapter for the shared daily-bar conformance subset.

The adapter only normalizes already-produced, credential-free LEAN backtest evidence.
It does not launch LEAN, place orders, grant paper/live authority, or reinterpret
candidate-native semantics outside the explicit A1 contract.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

from .conformance import canonical_receipt_hash, validate_receipt, validate_runtime_contract


class LeanA1AdapterError(ValueError):
    """Raised when LEAN evidence cannot be normalized without semantic guessing."""


_STATUS_MAP = {
    "SUBMITTED": "SUBMITTED",
    "NEW": "SUBMITTED",
    "ACCEPTED": "ACCEPTED",
    "PARTIALLYFILLED": "PARTIALLY_FILLED",
    "PARTIALLY_FILLED": "PARTIALLY_FILLED",
    "FILLED": "FILLED",
    "CANCELED": "CANCELLED",
    "CANCELLED": "CANCELLED",
    "INVALID": "REJECTED",
    "REJECTED": "REJECTED",
}


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _ordered_unique_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event["event_id"])
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise LeanA1AdapterError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(
        seen.values(),
        key=lambda event: (event["event_time"], int(event["sequence"]), event["event_id"]),
    )


def _normalized_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(dict(fixture))
    normalized["events"] = _ordered_unique_events(list(fixture.get("events", [])))
    normalized["intents"] = sorted(
        (dict(item) for item in fixture.get("intents", [])),
        key=lambda intent: (intent["created_at"], intent["intent_id"]),
    )
    return normalized


def _normalize_status(value: Any) -> str:
    token = str(value).replace(" ", "").replace("-", "_").upper()
    try:
        return _STATUS_MAP[token]
    except KeyError as exc:
        raise LeanA1AdapterError(f"unsupported LEAN order status: {value!r}") from exc


def _intent_index(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw_intents = list(fixture.get("intents", []))
    intents = {str(item["intent_id"]): dict(item) for item in raw_intents}
    if len(intents) != len(raw_intents):
        raise LeanA1AdapterError("duplicate intent_id in fixture")
    return intents


def normalize_lean_daily_result(
    raw: Mapping[str, Any],
    fixture: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    """Normalize one LEAN result for the reference simulator's initial subset.

    Supported subset: deterministic daily-bar BUY/SELL market intents, candidate-reported
    fills/fees, and terminal cash/equity/NAV. Candidate-native order/fill IDs are used only
    to prove lineage, then replaced by deterministic finance-quant semantic identities.
    Unsupported native states or ledger classes fail closed.
    """
    validate_runtime_contract(contract)
    if raw.get("engine") != "LEAN":
        raise LeanA1AdapterError("raw.engine must be LEAN")
    runtime_version = raw.get("engine_version")
    if not isinstance(runtime_version, str) or not runtime_version:
        raise LeanA1AdapterError("LEAN engine_version is required")

    intents = _intent_index(fixture)
    raw_events = list(fixture.get("events", []))
    events = {str(item["event_id"]): dict(item) for item in raw_events}
    if len(events) != len(raw_events):
        unique = _ordered_unique_events(raw_events)
        events = {str(item["event_id"]): item for item in unique}

    orders: list[dict[str, Any]] = []
    order_intents: dict[str, str] = {}
    normalized_order_ids: set[str] = set()
    for raw_order in raw.get("orders", []):
        native_order_id = str(raw_order["order_id"])
        intent_id = str(raw_order["intent_id"])
        if intent_id not in intents:
            raise LeanA1AdapterError(f"order references unknown intent_id: {intent_id}")
        if native_order_id in order_intents:
            raise LeanA1AdapterError(f"duplicate LEAN order_id: {native_order_id}")
        order_intents[native_order_id] = intent_id
        order_id = f"order:{intent_id}"
        if order_id in normalized_order_ids:
            raise LeanA1AdapterError(f"multiple LEAN orders for one intent: {intent_id}")
        normalized_order_ids.add(order_id)
        order = {
            "order_id": order_id,
            "intent_id": intent_id,
            "state": _normalize_status(raw_order["status"]),
            "quantity": str(raw_order["quantity"]),
        }
        if raw_order.get("filled_quantity") is not None:
            order["filled_quantity"] = str(raw_order["filled_quantity"])
        orders.append(order)

    fills: list[dict[str, Any]] = []
    native_to_normalized_fill: dict[str, str] = {}
    normalized_fill_ids: set[str] = set()
    for raw_fill in raw.get("fills", []):
        native_fill_id = str(raw_fill["fill_id"])
        if native_fill_id in native_to_normalized_fill:
            raise LeanA1AdapterError(f"duplicate LEAN fill_id: {native_fill_id}")
        native_order_id = str(raw_fill["order_id"])
        intent_id = str(raw_fill["intent_id"])
        if order_intents.get(native_order_id) != intent_id:
            raise LeanA1AdapterError("fill order/intent lineage is ambiguous")
        source_event_id = str(raw_fill["source_event_id"])
        event = events.get(source_event_id)
        if event is None:
            raise LeanA1AdapterError(f"fill references unknown source_event_id: {source_event_id}")
        intent = intents[intent_id]
        event_time = str(raw_fill["event_time"])
        if event_time != str(event["event_time"]):
            raise LeanA1AdapterError("fill event_time must match source fixture event")
        if event_time <= str(intent["created_at"]):
            raise LeanA1AdapterError("same-bar or pre-boundary fill violates FQ-PROP-015")
        if str(event["known_at"]) > event_time:
            raise LeanA1AdapterError("fill depends on future-known event")
        fill_id = f"fill:{intent_id}:{source_event_id}"
        if fill_id in normalized_fill_ids:
            raise LeanA1AdapterError("multiple candidate fills collapse to one semantic fill identity")
        normalized_fill_ids.add(fill_id)
        native_to_normalized_fill[native_fill_id] = fill_id
        fills.append(
            {
                "fill_id": fill_id,
                "order_id": f"order:{intent_id}",
                "intent_id": intent_id,
                "instrument_id": str(raw_fill["instrument_id"]),
                "event_time": event_time,
                "quantity": str(raw_fill["quantity"]),
                "price": str(raw_fill["price"]),
                "fee": str(raw_fill["fee"]),
                "slippage": str(raw_fill.get("slippage", "0")),
                "source_event_id": source_event_id,
            }
        )

    cash_ledger: list[dict[str, Any]] = []
    for entry in raw.get("cash_ledger", []):
        kind = str(entry.get("kind", "")).upper()
        if kind != "FILL":
            raise LeanA1AdapterError(f"unsupported A1 LEAN cash-ledger kind: {kind!r}")
        native_fill_id = str(entry.get("fill_id", ""))
        fill_id = native_to_normalized_fill.get(native_fill_id)
        if fill_id is None:
            raise LeanA1AdapterError("cash-ledger entry must reference a known LEAN fill_id")
        cash_ledger.append(
            {"entry_id": f"cash:{fill_id}", "kind": "FILL", "amount": str(entry["amount"])}
        )

    orders.sort(key=lambda order: order["intent_id"])
    fills.sort(key=lambda fill: (fill["intent_id"], fill["event_time"], fill["source_event_id"]))
    cash_ledger.sort(key=lambda entry: entry["entry_id"])
    positions = sorted(
        (dict(item) for item in raw.get("positions", [])),
        key=lambda item: str(item["instrument_id"]),
    )

    receipt: dict[str, Any] = {
        "contract_version": contract["schema_version"],
        "fixture_id": fixture["fixture_id"],
        "runtime": "lean",
        "runtime_version": runtime_version,
        "seed": seed,
        "status": str(raw.get("status", "COMPLETE")).upper(),
        "orders": orders,
        "fills": fills,
        "cash_ledger": cash_ledger,
        "positions": positions,
        "corporate_actions": [dict(item) for item in raw.get("corporate_actions", [])],
        "rejections": [dict(item) for item in raw.get("rejections", [])],
        "faults": [dict(item) for item in raw.get("faults", [])],
        "cash": str(raw["cash"]),
        "equity": str(raw["equity"]),
        "nav": str(raw["nav"]),
        "realized_pnl": str(raw.get("realized_pnl", "0")),
        "unrealized_pnl": str(raw.get("unrealized_pnl", "0")),
        "input_hash": _canonical_hash(_normalized_fixture(fixture)),
        "receipt_hash": "",
        "replay_lineage": dict(raw.get("replay_lineage", {"parent_receipt_hash": None})),
    }
    validate_receipt(receipt, contract)
    receipt["receipt_hash"] = canonical_receipt_hash(receipt, contract)
    return receipt
