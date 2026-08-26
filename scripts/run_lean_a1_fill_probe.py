"""Normalize pinned LEAN production fill-model evidence against the A1 reference oracle."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.differential import assert_normalized_receipts_conform
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference

D = Decimal

_EXPECTED_ENGINE = "LEAN"
_EXPECTED_SCOPE = "EquityFillModel.MarketOnOpenFill"
_TRACE_PREFIX = "TRACE::"


def _instant(value: str) -> datetime:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    result = datetime.fromisoformat(text)
    if result.tzinfo is None:
        raise ValueError(f"timestamp must be offset-aware: {value}")
    return result.astimezone(timezone.utc)


def load_probe_result(path: Path) -> dict[str, Any]:
    """Extract exactly one LEAN result object and fail closed on unknown stdout."""
    text = path.read_text(encoding="utf-8")
    candidates: list[dict[str, Any]] = []

    try:
        whole = json.loads(text)
    except json.JSONDecodeError:
        whole = None
    if isinstance(whole, dict):
        candidates.append(whole)
    else:
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(_TRACE_PREFIX):
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "unexpected non-JSON LEAN probe stdout; only TRACE:: diagnostics are permitted"
                ) from exc
            if not isinstance(value, dict):
                raise ValueError("LEAN probe JSON stdout entries must be objects")
            candidates.append(value)

    matches = [
        value
        for value in candidates
        if value.get("engine") == _EXPECTED_ENGINE
        and value.get("probe_scope") == _EXPECTED_SCOPE
    ]
    if len(matches) != 1 or len(candidates) != 1:
        raise ValueError(
            "probe output must contain exactly one LEAN EquityFillModel.MarketOnOpenFill JSON object; "
            f"found {len(matches)} matching of {len(candidates)} JSON object(s)"
        )
    return matches[0]


def build_raw_lean_result(
    probe: Mapping[str, Any], fixture: Mapping[str, Any], pin: Mapping[str, Any]
) -> dict[str, Any]:
    if probe.get("engine") != _EXPECTED_ENGINE:
        raise ValueError("probe engine must be LEAN")
    if probe.get("probe_scope") != _EXPECTED_SCOPE:
        raise ValueError("unexpected LEAN probe scope")
    if str(probe.get("status", "")).upper() != "FILLED":
        raise ValueError(f"LEAN probe did not fill: {probe.get('status')!r}")
    if pin.get("candidate") != "LEAN" or pin.get("runtime_disposition") != "PENDING":
        raise ValueError("LEAN pin must remain a pending A1 candidate")
    if pin.get("credentials_required") is not False or pin.get("cli_used") is not False:
        raise ValueError("A1 LEAN probe must remain credential-free and CLI-free")

    intents = list(fixture.get("intents", []))
    if len(intents) != 1:
        raise ValueError("initial LEAN production probe requires exactly one intent")
    intent = dict(intents[0])
    source_event_id = str(probe["source_event_id"])
    events = [dict(item) for item in fixture.get("events", [])]
    sources = [item for item in events if str(item["event_id"]) == source_event_id]
    if len(sources) != 1:
        raise ValueError("probe source event must identify exactly one fixture event")
    source = sources[0]
    if _instant(str(probe["fill_time"])) != _instant(str(source["event_time"])):
        raise ValueError("LEAN fill time must coincide with the contracted source event")
    if str(probe["instrument_id"]) != str(intent["instrument_id"]):
        raise ValueError("LEAN fill instrument must match the finance-quant intent")

    quantity = D(str(probe["fill_quantity"]))
    requested = D(str(intent["quantity"]))
    side = str(intent["side"]).upper()
    expected_signed = requested if side == "BUY" else -requested if side == "SELL" else None
    if expected_signed is None:
        raise ValueError(f"unsupported side: {side}")
    if quantity != expected_signed:
        raise ValueError("initial LEAN probe must fill the exact requested signed quantity")

    price = D(str(probe["fill_price"]))
    fee_per_unit = D(str(fixture.get("fee_per_unit", "0")))
    fee = abs(quantity) * fee_per_unit
    cash_delta = -(quantity * price) - fee if side == "BUY" else abs(quantity) * price - fee
    initial_cash = D(str(fixture.get("initial_cash", "0")))
    cash = initial_cash + cash_delta

    instrument = str(intent["instrument_id"])
    marks = [
        D(str(item.get("payload", {}).get("close", item.get("payload", {}).get("open", "0"))))
        for item in events
        if str(item["instrument_id"]) == instrument
        and str(item["known_at"]) <= str(item["event_time"])
    ]
    if not marks:
        raise ValueError("fixture lacks a PIT-safe terminal mark")
    equity = quantity * marks[-1]
    nav = cash + equity

    native_order_id = "lean-probe-order-1"
    native_fill_id = "lean-probe-fill-1"
    return {
        "engine": "LEAN",
        "engine_version": str(pin["source_commit"]),
        "status": "COMPLETE",
        "orders": [
            {
                "order_id": native_order_id,
                "intent_id": intent["intent_id"],
                "status": probe["status"],
                "quantity": str(requested),
                "filled_quantity": str(abs(quantity)),
            }
        ],
        "fills": [
            {
                "fill_id": native_fill_id,
                "order_id": native_order_id,
                "intent_id": intent["intent_id"],
                "instrument_id": instrument,
                "event_time": source["event_time"],
                "quantity": str(abs(quantity)),
                "price": str(price),
                "fee": str(fee),
                "slippage": "0",
                "source_event_id": source_event_id,
            }
        ],
        "cash_ledger": [
            {"fill_id": native_fill_id, "kind": "FILL", "amount": str(cash_delta)}
        ],
        "positions": [{"instrument_id": instrument, "quantity": str(quantity)}],
        "corporate_actions": [],
        "rejections": [],
        "faults": [],
        "cash": str(cash),
        "equity": str(equity),
        "nav": str(nav),
        "realized_pnl": "0",
        "unrealized_pnl": str(nav - initial_cash),
        "replay_lineage": {"parent_receipt_hash": None, "committed_event_count": len(events)},
    }


def verify_probe(
    probe: Mapping[str, Any], fixture: Mapping[str, Any], pin: Mapping[str, Any]
) -> dict[str, Any]:
    contract = load_runtime_contract()
    raw = build_raw_lean_result(probe, fixture, pin)
    reference = run_daily_reference(fixture, contract)
    candidate = normalize_lean_daily_result(raw, fixture, contract)
    assert_normalized_receipts_conform(reference, candidate, contract)
    return {
        "issue": 15,
        "phase": "A1",
        "candidate": "LEAN",
        "candidate_source_commit": pin["source_commit"],
        "evidence_mode": pin["evidence_mode"],
        "fixture_id": fixture["fixture_id"],
        "probe": dict(probe),
        "reference_receipt_hash": reference["receipt_hash"],
        "candidate_receipt_hash": candidate["receipt_hash"],
        "semantic_conformance": "PASS",
        "runtime_disposition": "PENDING",
        "authority": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--pin", type=Path, required=True)
    parser.add_argument("--probe-result", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    pin = json.loads(args.pin.read_text(encoding="utf-8"))
    probe = load_probe_result(args.probe_result)
    evidence = verify_probe(probe, fixture, pin)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())