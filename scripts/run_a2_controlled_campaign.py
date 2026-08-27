"""Run one controlled A2 production-LEAN session and emit deterministic aggregate evidence."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.differential import assert_normalized_receipts_conform
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference
from finance_quant.trader.account import VirtualAccountStore
from finance_quant.trader.execution import A2_LEAN_COMMIT, commit_lean_session
from scripts.run_lean_a1_fill_probe import build_raw_lean_result, load_probe_result


def build_campaign_receipt(
    *,
    spec: Mapping[str, Any],
    fixture: Mapping[str, Any],
    strategy_risk: Mapping[str, Any],
    pin: Mapping[str, Any],
    probe: Mapping[str, Any],
    db_path: Path,
) -> dict[str, Any]:
    if pin.get("source_commit") != A2_LEAN_COMMIT:
        raise ValueError("controlled A2 campaign must use the A1-selected LEAN pin")
    if strategy_risk.get("authority") != "NONE":
        raise ValueError("controlled A2 campaign must run with authority NONE")
    if strategy_risk.get("risk_decision", {}).get("status") != "APPROVED":
        raise ValueError("controlled A2 campaign requires an approved mechanical risk decision")

    contract = load_runtime_contract()
    raw = build_raw_lean_result(probe, fixture, pin)
    reference = run_daily_reference(fixture, contract)
    candidate = normalize_lean_daily_result(raw, fixture, contract)
    assert_normalized_receipts_conform(reference, candidate, contract)

    with VirtualAccountStore(db_path, initial_cash=spec["initial_cash"]) as store:
        session = commit_lean_session(
            store,
            candidate,
            fixture,
            session_id=str(spec["session_id"]),
            strategy_hash=str(strategy_risk["strategy_hash"]),
            risk_hash=str(strategy_risk["risk_hash"]),
        )
        state_hash = store.state_hash()
        state = store.authoritative_state()
        instrument = str(spec["instrument_id"])
        terminal_event = list(fixture["events"])[-1]
        nav = store.nav({instrument: terminal_event["payload"]["close"]})
        if nav["nav"] != str(candidate["nav"]):
            raise ValueError("finance-quant NAV does not match normalized execution NAV")
        if len(store.session_receipts()) != 1:
            raise ValueError("controlled campaign must commit exactly one authoritative session receipt")

    return {
        "schema_version": "1.0.0",
        "issue": 16,
        "phase": "A2",
        "fixture_id": str(fixture["fixture_id"]),
        "session_id": str(spec["session_id"]),
        "strategy_id": str(strategy_risk["strategy_id"]),
        "strategy_spec_hash": str(strategy_risk["strategy_spec_hash"]),
        "strategy_hash": str(strategy_risk["strategy_hash"]),
        "risk_hash": str(strategy_risk["risk_hash"]),
        "risk_status": str(strategy_risk["risk_decision"]["status"]),
        "runtime": "LEAN",
        "runtime_commit": A2_LEAN_COMMIT,
        "reference_receipt_hash": str(reference["receipt_hash"]),
        "candidate_receipt_hash": str(candidate["receipt_hash"]),
        "session_receipt_hash": session.receipt_hash,
        "initial_state_hash": session.initial_state_hash,
        "terminal_state_hash": session.terminal_state_hash,
        "authoritative_state_hash": state_hash,
        "cash": str(state["cash"]),
        "positions": state["positions"],
        "nav": nav["nav"],
        "differential_conformance": "PASS",
        "authority": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--strategy-risk", type=Path, required=True)
    parser.add_argument("--pin", type=Path, required=True)
    parser.add_argument("--probe-result", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    receipt = build_campaign_receipt(
        spec=json.loads(args.spec.read_text(encoding="utf-8")),
        fixture=json.loads(args.fixture.read_text(encoding="utf-8")),
        strategy_risk=json.loads(args.strategy_risk.read_text(encoding="utf-8")),
        pin=json.loads(args.pin.read_text(encoding="utf-8")),
        probe=load_probe_result(args.probe_result),
        db_path=args.db,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
