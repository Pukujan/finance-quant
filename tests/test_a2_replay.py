from __future__ import annotations

import json
from pathlib import Path

import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.differential import assert_normalized_receipts_conform
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference
from finance_quant.trader.evidence import ReplayableAccountStore, commit_replayable_session, replay_authoritative_store
from finance_quant.trader.execution import A2_LEAN_COMMIT
from finance_quant.trader.stateful import plan_stateful_session, rebase_incremental_execution
from scripts.run_lean_a1_fill_probe import build_raw_lean_result

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / "contracts/execution/lean-a1-candidate-pin-v1.json").read_text())


def _probe(session: int):
    if session == 1:
        return {
            "engine": "LEAN", "probe_scope": "EquityFillModel.MarketOnOpenFill", "order_type": "MarketOnOpen",
            "status": "Filled", "fill_quantity": "5", "fill_price": "13",
            "fill_time": "2026-06-03T13:30:00+00:00", "source_event_id": "bar-3-open",
            "instrument_id": "AAA", "fill_message": "",
        }
    return {
        "engine": "LEAN", "probe_scope": "EquityFillModel.MarketOnOpenFill", "order_type": "MarketOnOpen",
        "status": "Filled", "fill_quantity": "-2", "fill_price": "10",
        "fill_time": "2026-06-08T13:30:00+00:00", "source_event_id": "bar-6-open",
        "instrument_id": "AAA", "fill_message": "",
    }


def _spec(session: int):
    path = "a2-controlled-baseline-v1.json" if session == 1 else "a2-controlled-baseline-v1-session-2.json"
    return json.loads((ROOT / "fixtures/trader" / path).read_text())


def _run(store, session: int):
    spec = _spec(session)
    fixture, plan = plan_stateful_session(store, spec)
    raw = build_raw_lean_result(_probe(session), fixture, PIN)
    contract = load_runtime_contract()
    reference = run_daily_reference(fixture, contract)
    incremental = normalize_lean_daily_result(raw, fixture, contract)
    assert_normalized_receipts_conform(reference, incremental, contract)
    rebased = rebase_incremental_execution(store, incremental, fixture)
    receipt = commit_replayable_session(
        store, rebased, fixture,
        session_id=spec["session_id"], strategy_hash=plan["strategy_hash"], risk_hash=plan["risk_hash"],
        runtime_commit=A2_LEAN_COMMIT,
    )
    return receipt, plan


def test_fq_prop_025_026_two_session_restart_and_exact_evidence_replay(tmp_path):
    source = tmp_path / "source.db"
    with ReplayableAccountStore(source, initial_cash="1000") as store:
        first, _ = _run(store, 1)
        assert store.authoritative_state()["cash"] == "935"
        assert store.authoritative_state()["positions"] == [{"instrument_id": "AAA", "quantity": "5"}]
    with ReplayableAccountStore(source) as reopened:
        assert reopened.state_hash() == first.terminal_state_hash
        second, plan2 = _run(reopened, 2)
        assert plan2["risk_state"]["gross_exposure"] > 0
        assert second.parent_receipt_hash == first.receipt_hash
        assert second.initial_state_hash == first.terminal_state_hash
        assert reopened.authoritative_state()["cash"] == "955"
        assert reopened.authoritative_state()["positions"] == [{"instrument_id": "AAA", "quantity": "3"}]
        expected_state = reopened.state_hash()
        expected_receipts = [item["receipt_hash"] for item in reopened.session_receipts()]
        assert len(reopened.session_evidence()) == 2

    replay = replay_authoritative_store(source, tmp_path / "replay.db")
    assert replay["status"] == "PASS"
    assert replay["terminal_state_hash"] == expected_state
    assert replay["session_receipt_hashes"] == expected_receipts


def test_fq_prop_028_evidence_insert_failure_rolls_back_session_and_account(tmp_path, monkeypatch):
    path = tmp_path / "account.db"
    with ReplayableAccountStore(path, initial_cash="1000") as store:
        spec = _spec(1)
        fixture, plan = plan_stateful_session(store, spec)
        raw = build_raw_lean_result(_probe(1), fixture, PIN)
        incremental = normalize_lean_daily_result(raw, fixture, load_runtime_contract())
        rebased = rebase_incremental_execution(store, incremental, fixture)
        before = store.state_hash()

        def fail(_receipt):
            raise RuntimeError("simulated evidence persistence crash")

        monkeypatch.setattr(store, "_insert_staged_evidence", fail)
        with pytest.raises(RuntimeError, match="evidence persistence"):
            commit_replayable_session(
                store, rebased, fixture,
                session_id=spec["session_id"], strategy_hash=plan["strategy_hash"], risk_hash=plan["risk_hash"],
                runtime_commit=A2_LEAN_COMMIT,
            )
        assert store.state_hash() == before
        assert store.session_receipts() == []
        assert store.session_evidence() == []
