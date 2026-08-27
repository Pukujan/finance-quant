from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from finance_quant.execution.conformance import canonical_receipt_hash, load_runtime_contract
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.trader.account import VirtualAccountStore
from finance_quant.trader.execution import ExecutionApplicationError, commit_lean_session
from scripts.prepare_a2_controlled_fixture import prepare_controlled_fixture
from scripts.run_lean_a1_fill_probe import build_raw_lean_result

ROOT = Path(__file__).resolve().parents[1]


def _probe():
    return {
        "engine": "LEAN",
        "probe_scope": "EquityFillModel.MarketOnOpenFill",
        "order_type": "MarketOnOpen",
        "status": "Filled",
        "fill_quantity": "5",
        "fill_price": "13",
        "fill_time": "2026-06-03T13:30:00+00:00",
        "source_event_id": "bar-3-open",
        "instrument_id": "AAA",
        "fill_message": "",
    }


def _execution():
    spec = json.loads((ROOT / "fixtures/trader/a2-controlled-baseline-v1.json").read_text())
    pin = json.loads((ROOT / "contracts/execution/lean-a1-candidate-pin-v1.json").read_text())
    fixture, evidence = prepare_controlled_fixture(spec)
    raw = build_raw_lean_result(_probe(), fixture, pin)
    receipt = normalize_lean_daily_result(raw, fixture, load_runtime_contract())
    return spec, fixture, evidence, receipt


def _rehash(receipt):
    changed = deepcopy(receipt)
    changed["receipt_hash"] = ""
    changed["receipt_hash"] = canonical_receipt_hash(changed, load_runtime_contract())
    return changed


def test_chaos_dropped_cash_ledger_rolls_back_all_account_effects(tmp_path):
    spec, fixture, evidence, receipt = _execution()
    bad = deepcopy(receipt)
    bad["cash_ledger"] = []
    bad = _rehash(bad)
    with VirtualAccountStore(tmp_path / "account.db", initial_cash=spec["initial_cash"]) as store:
        before = store.state_hash()
        with pytest.raises(ExecutionApplicationError, match="cash ledger"):
            commit_lean_session(
                store,
                bad,
                fixture,
                session_id=spec["session_id"],
                strategy_hash=evidence["strategy_hash"],
                risk_hash=evidence["risk_hash"],
            )
        assert store.state_hash() == before
        assert store.session_receipts() == []


def test_chaos_dropped_fill_with_filled_order_rolls_back(tmp_path):
    spec, fixture, evidence, receipt = _execution()
    bad = deepcopy(receipt)
    bad["fills"] = []
    bad["cash_ledger"] = []
    bad = _rehash(bad)
    with VirtualAccountStore(tmp_path / "account.db", initial_cash=spec["initial_cash"]) as store:
        before = store.state_hash()
        with pytest.raises(ExecutionApplicationError, match="order state"):
            commit_lean_session(
                store,
                bad,
                fixture,
                session_id=spec["session_id"],
                strategy_hash=evidence["strategy_hash"],
                risk_hash=evidence["risk_hash"],
            )
        assert store.state_hash() == before
        assert store.session_receipts() == []


def test_chaos_event_reorder_is_idempotent_but_conflicting_duplicate_fails_closed(tmp_path):
    spec, fixture, evidence, receipt = _execution()
    with VirtualAccountStore(tmp_path / "account.db", initial_cash=spec["initial_cash"]) as store:
        first = commit_lean_session(
            store,
            receipt,
            fixture,
            session_id=spec["session_id"],
            strategy_hash=evidence["strategy_hash"],
            risk_hash=evidence["risk_hash"],
        )
        reordered = deepcopy(fixture)
        reordered["events"] = list(reversed(reordered["events"]))
        retry = commit_lean_session(
            store,
            receipt,
            reordered,
            session_id=spec["session_id"],
            strategy_hash=evidence["strategy_hash"],
            risk_hash=evidence["risk_hash"],
        )
        assert retry == first
        before = store.state_hash()
        conflicting = deepcopy(reordered)
        altered = deepcopy(conflicting["events"][0])
        altered["payload"]["open"] = "999"
        conflicting["events"].append(altered)
        with pytest.raises(ExecutionApplicationError, match="ambiguous duplicate"):
            commit_lean_session(
                store,
                receipt,
                conflicting,
                session_id="conflicting-session",
                strategy_hash=evidence["strategy_hash"],
                risk_hash=evidence["risk_hash"],
            )
        assert store.state_hash() == before
