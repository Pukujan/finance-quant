"""Atomic A2 ingestion of normalized LEAN execution evidence."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from finance_quant.execution.conformance import (
    canonical_receipt_hash,
    load_runtime_contract,
    validate_receipt,
)

from .account import AccountInvariantError, VirtualAccountStore
from .session import SessionReceipt, SessionReceiptError, build_session_receipt, validate_session_chain

A2_LEAN_COMMIT = "185c691b89f28bd68e48d53c02147415134975f0"
D = Decimal


class ExecutionApplicationError(ValueError):
    """Raised when normalized runtime evidence cannot safely become account truth."""


def _sha256(value: str, *, field: str) -> str:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ExecutionApplicationError(f"{field} must be lowercase sha256")
    return value


def _decimal(value: object, *, field: str) -> Decimal:
    try:
        result = D(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ExecutionApplicationError(f"{field} must be a decimal") from exc
    if not result.is_finite():
        raise ExecutionApplicationError(f"{field} must be finite")
    return result


def _ordered_unique_events(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for raw in events:
        event = dict(raw)
        event_id = str(event["event_id"])
        prior = seen.get(event_id)
        if prior is not None and prior != event:
            raise ExecutionApplicationError(f"ambiguous duplicate event_id: {event_id}")
        seen[event_id] = event
    return sorted(seen.values(), key=lambda e: (e["event_time"], int(e["sequence"]), e["event_id"]))


def _fixture_hash(fixture: Mapping[str, Any]) -> str:
    normalized = dict(fixture)
    normalized["events"] = _ordered_unique_events(list(fixture.get("events", [])))
    normalized["intents"] = sorted(
        (dict(item) for item in fixture.get("intents", [])),
        key=lambda i: (i["created_at"], i["intent_id"]),
    )
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _intent_index(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw = [dict(item) for item in fixture.get("intents", [])]
    result = {str(item["intent_id"]): item for item in raw}
    if len(result) != len(raw):
        raise ExecutionApplicationError("fixture contains duplicate intent_id")
    return result


def _validate_execution_receipt(
    receipt: Mapping[str, Any],
    fixture: Mapping[str, Any],
    *,
    runtime_commit: str,
) -> None:
    if runtime_commit != A2_LEAN_COMMIT:
        raise ExecutionApplicationError("runtime commit is not the A1-selected LEAN pin")
    contract = load_runtime_contract()
    validate_receipt(receipt, contract)
    if receipt.get("receipt_hash") != canonical_receipt_hash(receipt, contract):
        raise ExecutionApplicationError("execution receipt_hash mismatch")
    if receipt.get("runtime") != "lean":
        raise ExecutionApplicationError("A2 execution receipt must use normalized runtime 'lean'")
    if receipt.get("status") != "COMPLETE":
        raise ExecutionApplicationError("A2 initial ingestion requires COMPLETE execution receipt")
    if receipt.get("input_hash") != _fixture_hash(fixture):
        raise ExecutionApplicationError("execution receipt is not bound to the supplied fixture")
    for field in ("corporate_actions", "faults"):
        if receipt.get(field):
            raise ExecutionApplicationError(f"A2 initial ingestion does not support non-empty {field}")
    if receipt.get("rejections"):
        raise ExecutionApplicationError("A2 initial ingestion does not yet materialize rejected orders")


def _apply_execution_effects(
    store: VirtualAccountStore,
    receipt: Mapping[str, Any],
    fixture: Mapping[str, Any],
    *,
    session_id: str,
) -> None:
    intents = _intent_index(fixture)
    expected_orders: dict[str, Mapping[str, Any]] = {}
    for raw_order in receipt.get("orders", []):
        if not isinstance(raw_order, Mapping):
            raise ExecutionApplicationError("execution order must be an object")
        intent_id = str(raw_order.get("intent_id", ""))
        intent = intents.get(intent_id)
        if intent is None:
            raise ExecutionApplicationError(f"execution order references unknown intent: {intent_id}")
        order_id = str(raw_order.get("order_id", ""))
        if order_id != f"order:{intent_id}":
            raise ExecutionApplicationError("execution order_id is not the deterministic semantic identity")
        if order_id in expected_orders:
            raise ExecutionApplicationError("duplicate execution order identity")
        state = str(raw_order.get("state", ""))
        if state not in {"ACCEPTED", "PARTIALLY_FILLED", "FILLED"}:
            raise ExecutionApplicationError(f"unsupported A2 execution order state: {state}")
        if _decimal(raw_order.get("quantity"), field="order.quantity") != _decimal(
            intent.get("quantity"), field="intent.quantity"
        ):
            raise ExecutionApplicationError("execution order quantity differs from immutable intent")
        side = str(intent.get("side", "")).upper()
        if side not in {"BUY", "SELL"}:
            raise ExecutionApplicationError("fixture intent side must be BUY or SELL")
        store.submit_order(
            order_id=order_id,
            intent_id=intent_id,
            session_id=session_id,
            instrument_id=str(intent["instrument_id"]),
            side=side,
            quantity=intent["quantity"],
            created_at=str(intent["created_at"]),
        )
        expected_orders[order_id] = raw_order

    expected_fill_ids: set[str] = set()
    for raw_fill in receipt.get("fills", []):
        if not isinstance(raw_fill, Mapping):
            raise ExecutionApplicationError("execution fill must be an object")
        intent_id = str(raw_fill.get("intent_id", ""))
        intent = intents.get(intent_id)
        if intent is None:
            raise ExecutionApplicationError(f"execution fill references unknown intent: {intent_id}")
        order_id = str(raw_fill.get("order_id", ""))
        if order_id not in expected_orders or order_id != f"order:{intent_id}":
            raise ExecutionApplicationError("execution fill order/intent lineage is invalid")
        instrument = str(raw_fill.get("instrument_id", ""))
        if instrument != str(intent["instrument_id"]):
            raise ExecutionApplicationError("execution fill instrument differs from immutable intent")
        source_event_id = str(raw_fill.get("source_event_id", ""))
        fill_id = str(raw_fill.get("fill_id", ""))
        if fill_id != f"fill:{intent_id}:{source_event_id}":
            raise ExecutionApplicationError("execution fill_id is not the deterministic semantic identity")
        if fill_id in expected_fill_ids:
            raise ExecutionApplicationError("duplicate execution fill identity")
        expected_fill_ids.add(fill_id)
        store.apply_fill(
            fill_id=fill_id,
            order_id=order_id,
            session_id=session_id,
            instrument_id=instrument,
            quantity=raw_fill["quantity"],
            price=raw_fill["price"],
            fee=raw_fill["fee"],
            event_time=str(raw_fill["event_time"]),
            source_event_id=source_event_id,
        )

    state = store.authoritative_state()
    actual_orders = {str(item["order_id"]): item for item in state["orders"]}
    for order_id, expected in expected_orders.items():
        actual = actual_orders.get(order_id)
        if actual is None:
            raise ExecutionApplicationError("execution order disappeared from account state")
        if str(actual["state"]) != str(expected["state"]):
            raise ExecutionApplicationError("account order state does not match execution receipt")
        if expected.get("filled_quantity") is not None and _decimal(
            actual["filled_quantity"], field="account.filled_quantity"
        ) != _decimal(expected["filled_quantity"], field="receipt.filled_quantity"):
            raise ExecutionApplicationError("account filled quantity does not match execution receipt")

    account_ledger = {
        str(item["fill_id"]): {
            "entry_id": str(item["entry_id"]),
            "kind": str(item["kind"]),
            "amount": _decimal(item["amount"], field="account.cash_ledger.amount"),
        }
        for item in state["cash_ledger"]
        if str(item["fill_id"]) in expected_fill_ids
    }
    receipt_ledger: dict[str, dict[str, object]] = {}
    for item in receipt.get("cash_ledger", []):
        if not isinstance(item, Mapping):
            raise ExecutionApplicationError("execution cash-ledger entry must be an object")
        entry_id = str(item.get("entry_id", ""))
        if not entry_id.startswith("cash:fill:"):
            raise ExecutionApplicationError("execution cash-ledger identity is not normalized")
        fill_id = entry_id.removeprefix("cash:")
        if fill_id not in expected_fill_ids:
            raise ExecutionApplicationError("execution cash-ledger entry references unknown fill")
        receipt_ledger[fill_id] = {
            "entry_id": entry_id,
            "kind": str(item.get("kind", "")),
            "amount": _decimal(item.get("amount"), field="receipt.cash_ledger.amount"),
        }
    if account_ledger != receipt_ledger:
        raise ExecutionApplicationError("account cash ledger does not match execution receipt")

    store.assert_terminal_matches(cash=receipt["cash"], positions=list(receipt.get("positions", [])))


def _existing_session_matches(
    existing: SessionReceipt,
    *,
    input_hash: str,
    strategy_hash: str,
    risk_hash: str,
    execution_hash: str,
    runtime_commit: str,
) -> bool:
    return (
        existing.input_hash == input_hash
        and existing.strategy_hash == strategy_hash
        and existing.risk_hash == risk_hash
        and existing.execution_hash == execution_hash
        and existing.runtime == "LEAN"
        and existing.runtime_commit == runtime_commit
        and existing.authority == "NONE"
        and existing.status == "COMPLETE"
    )


def commit_lean_session(
    store: VirtualAccountStore,
    receipt: Mapping[str, Any],
    fixture: Mapping[str, Any],
    *,
    session_id: str,
    strategy_hash: str,
    risk_hash: str,
    runtime_commit: str = A2_LEAN_COMMIT,
) -> SessionReceipt:
    """Atomically commit validated LEAN effects and their authoritative SessionReceipt."""
    if not session_id:
        raise ExecutionApplicationError("session_id must be non-empty")
    strategy_hash = _sha256(strategy_hash, field="strategy_hash")
    risk_hash = _sha256(risk_hash, field="risk_hash")
    _validate_execution_receipt(receipt, fixture, runtime_commit=runtime_commit)
    input_hash = _sha256(str(receipt["input_hash"]), field="input_hash")
    execution_hash = _sha256(str(receipt["receipt_hash"]), field="execution_hash")

    existing_raw = store.get_session_receipt(session_id)
    if existing_raw is not None:
        existing = SessionReceipt.from_dict(existing_raw)
        if not _existing_session_matches(
            existing,
            input_hash=input_hash,
            strategy_hash=strategy_hash,
            risk_hash=risk_hash,
            execution_hash=execution_hash,
            runtime_commit=runtime_commit,
        ):
            raise ExecutionApplicationError("conflicting reuse of committed session_id")
        return existing

    previous_raw = store.latest_session_receipt()
    previous = None if previous_raw is None else SessionReceipt.from_dict(previous_raw)
    initial_state_hash = store.state_hash()
    if previous is not None and initial_state_hash != previous.terminal_state_hash:
        raise ExecutionApplicationError("durable account state diverged from latest SessionReceipt")
    session_number = 1 if previous is None else previous.session_number + 1

    try:
        with store.transaction():
            _apply_execution_effects(store, receipt, fixture, session_id=session_id)
            terminal_state_hash = store.state_hash()
            current = build_session_receipt(
                session_id=session_id,
                session_number=session_number,
                parent_receipt_hash=None if previous is None else previous.receipt_hash,
                initial_state_hash=initial_state_hash,
                terminal_state_hash=terminal_state_hash,
                input_hash=input_hash,
                strategy_hash=strategy_hash,
                risk_hash=risk_hash,
                execution_hash=execution_hash,
                runtime="LEAN",
                runtime_commit=runtime_commit,
                authority="NONE",
                status="COMPLETE",
            )
            validate_session_chain(previous, current)
            store.append_session_receipt(current)
    except (AccountInvariantError, SessionReceiptError) as exc:
        raise ExecutionApplicationError(str(exc)) from exc
    return current
