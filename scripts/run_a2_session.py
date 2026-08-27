from __future__ import annotations

import argparse
import json
from pathlib import Path

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.differential import assert_normalized_receipts_conform
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference
from finance_quant.trader.evidence import ReplayableAccountStore, commit_replayable_session
from finance_quant.trader.execution import A2_LEAN_COMMIT
from finance_quant.trader.stateful import rebase_incremental_execution
from scripts.run_lean_a1_fill_probe import build_raw_lean_result, load_probe_result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pin", type=Path, required=True)
    parser.add_argument("--probe-result", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--execution-out", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    pin = json.loads(args.pin.read_text(encoding="utf-8"))
    if pin.get("source_commit") != A2_LEAN_COMMIT:
        raise SystemExit("A2 session runtime pin mismatch")
    probe = load_probe_result(args.probe_result)
    contract = load_runtime_contract()
    raw = build_raw_lean_result(probe, fixture, pin)
    reference = run_daily_reference(fixture, contract)
    incremental = normalize_lean_daily_result(raw, fixture, contract)
    assert_normalized_receipts_conform(reference, incremental, contract)

    with ReplayableAccountStore(args.db) as store:
        rebased = rebase_incremental_execution(store, incremental, fixture)
        session = commit_replayable_session(
            store,
            rebased,
            fixture,
            session_id=str(spec["session_id"]),
            strategy_hash=str(plan["strategy_hash"]),
            risk_hash=str(plan["risk_hash"]),
            runtime_commit=A2_LEAN_COMMIT,
        )
        state = store.authoritative_state()
        receipt = {
            "schema_version": "1.0.0",
            "issue": 16,
            "phase": "A2",
            "session_id": session.session_id,
            "session_number": session.session_number,
            "parent_receipt_hash": session.parent_receipt_hash,
            "session_receipt_hash": session.receipt_hash,
            "initial_state_hash": session.initial_state_hash,
            "terminal_state_hash": session.terminal_state_hash,
            "incremental_reference_hash": reference["receipt_hash"],
            "incremental_candidate_hash": incremental["receipt_hash"],
            "stateful_execution_hash": rebased["receipt_hash"],
            "strategy_hash": plan["strategy_hash"],
            "risk_hash": plan["risk_hash"],
            "account_state_hash": store.state_hash(),
            "cash": state["cash"],
            "positions": state["positions"],
            "differential_conformance": "PASS",
            "authority": "NONE",
        }
    args.execution_out.parent.mkdir(parents=True, exist_ok=True)
    args.execution_out.write_text(json.dumps(rebased, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
