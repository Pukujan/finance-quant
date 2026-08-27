from __future__ import annotations

from copy import deepcopy

import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.trader.account import VirtualAccountStore
from finance_quant.trader.execution import A2_LEAN_COMMIT, ExecutionApplicationError, commit_lean_session


def _fixture(*, intent_id: str = "intent-1", side: str = "BUY", quantity: str = "5", day: int = 1):
    return {
        "fixture_id": f"a2-session-{intent_id}",
        "initial_cash": "1000",
        "fee_per_unit": "1",
        "events": [
            {
                "event_id": f"bar-{day}",
                "instrument_id": "AAA",
                "event_time": f"2026-01-{day:02d}T00:00:00Z",
                "known_at": f"2026-01-{day:02d}T00:00:00Z",
                "sequence": 1,
                "payload": {"open": "10", "close": "10", "liquidity": "10"},
            },
            {
                "event_id": f"bar-{day + 1}",
                "instrument_id": "AAA",
                "event_time": f"2026-01-{day + 1:02d}T00:00:00Z",
                "known_at": f"2026-01-{day + 1:02d}T00:00:00Z",
                "sequence": 2,
                "payload": {"open": "11", "close": "12", "liquidity": "10"},
            },
        ],
        "intents": [
            {
                "intent_id": intent_id,
                "instrument_id": "AAA",
                "created_at": f"2026-01-{day:02d}T00:00:00Z",
                "side": side,
                "quantity": quantity,
                "order_type": "MARKET",
            }
        ],
    }


def _raw_lean(
    fixture,
    *,
    cash: str,
    position: str,
    fill_price: str = "11",
    fee: str = "5",
):
    intent = fixture["intents"][0]
    intent_id = intent["intent_id"]
    source = fixture["events"][1]
    return {
        "engine": "LEAN",
        "engine_version": A2_LEAN_COMMIT,
        "status": "COMPLETE",
        "orders": [
            {
                "order_id": f"native-order-{intent_id}",
                "intent_id": intent_id,
                "status": "Filled",
                "quantity": intent["quantity"],
                "filled_quantity": intent["quantity"],
            }
        ],
        "fills": [
            {
                "fill_id": f"native-fill-{intent_id}",
                "order_id": f"native-order-{intent_id}",
                "intent_id": intent_id,
                "instrument_id": "AAA",
                "event_time": source["event_time"],
                "quantity": intent["quantity"],
                "price": fill_price,
                "fee": fee,
                "slippage": "0",
                "source_event_id": source["event_id"],
            }
        ],
        "cash_ledger": [
            {
                "entry_id": f"native-ledger-{intent_id}",
                "fill_id": f"native-fill-{intent_id}",
                "kind": "FILL",
                "amount": "-60" if intent["side"] == "BUY" else "17",
            }
        ],
        "positions": [{"instrument_id": "AAA", "quantity": position}],
        "corporate_actions": [],
        "rejections": [],
        "faults": [],
        "cash": cash,
        "equity": "60",
        "nav": "1000",
        "realized_pnl": "0",
        "unrealized_pnl": "0",
        "replay_lineage": {"parent_receipt_hash": None, "committed_event_count": 2},
    }


def _normalized_first():
    fixture = _fixture()
    raw = _raw_lean(fixture, cash="940", position="5")
    return fixture, normalize_lean_daily_result(raw, fixture, load_runtime_contract())


def test_lean_receipt_commits_account_and_authoritative_session_atomically(tmp_path):
    fixture, execution = _normalized_first()
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        receipt = commit_lean_session(
            store,
            execution,
            fixture,
            session_id="session-1",
            strategy_hash="1" * 64,
            risk_hash="2" * 64,
        )
        assert receipt.runtime == "LEAN"
        assert receipt.runtime_commit == A2_LEAN_COMMIT
        assert receipt.execution_hash == execution["receipt_hash"]
        assert receipt.terminal_state_hash == store.state_hash()
        assert store.authoritative_state()["cash"] == "940"
        assert store.authoritative_state()["positions"] == [{"instrument_id": "AAA", "quantity": "5"}]
        assert len(store.session_receipts()) == 1

        state_hash = store.state_hash()
        retry = commit_lean_session(
            store,
            execution,
            fixture,
            session_id="session-1",
            strategy_hash="1" * 64,
            risk_hash="2" * 64,
        )
        assert retry == receipt
        assert store.state_hash() == state_hash
        assert len(store.authoritative_state()["fills"]) == 1
        assert len(store.session_receipts()) == 1


def test_fq_prop_025_two_sessions_chain_exact_account_state(tmp_path):
    fixture1, execution1 = _normalized_first()
    path = tmp_path / "account.db"
    with VirtualAccountStore(path, initial_cash="1000") as store:
        first = commit_lean_session(
            store,
            execution1,
            fixture1,
            session_id="session-1",
            strategy_hash="1" * 64,
            risk_hash="2" * 64,
        )

        fixture2 = _fixture(intent_id="intent-2", side="SELL", quantity="2", day=3)
        raw2 = _raw_lean(fixture2, cash="957", position="3", fill_price="11", fee="5")
        raw2["cash_ledger"][0]["amount"] = "17"
        execution2 = normalize_lean_daily_result(raw2, fixture2, load_runtime_contract())
        second = commit_lean_session(
            store,
            execution2,
            fixture2,
            session_id="session-2",
            strategy_hash="3" * 64,
            risk_hash="4" * 64,
        )
        assert second.session_number == 2
        assert second.parent_receipt_hash == first.receipt_hash
        assert second.initial_state_hash == first.terminal_state_hash
        assert store.authoritative_state()["cash"] == "957"
        assert store.authoritative_state()["positions"] == [{"instrument_id": "AAA", "quantity": "3"}]

    with VirtualAccountStore(path) as reopened:
        receipts = reopened.session_receipts()
        assert len(receipts) == 2
        assert reopened.state_hash() == receipts[-1]["terminal_state_hash"]


def test_fq_prop_028_session_commit_rolls_back_account_if_receipt_persistence_fails(tmp_path, monkeypatch):
    fixture, execution = _normalized_first()
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        initial_hash = store.state_hash()

        def fail_receipt(_receipt):
            raise RuntimeError("simulated crash before authoritative receipt insert")

        monkeypatch.setattr(store, "append_session_receipt", fail_receipt)
        with pytest.raises(RuntimeError, match="simulated crash"):
            commit_lean_session(
                store,
                execution,
                fixture,
                session_id="session-1",
                strategy_hash="1" * 64,
                risk_hash="2" * 64,
            )
        assert store.state_hash() == initial_hash
        assert store.authoritative_state()["orders"] == []
        assert store.authoritative_state()["fills"] == []
        assert store.session_receipts() == []


def test_reconciliation_failure_rolls_back_entire_execution_receipt(tmp_path):
    fixture, execution = _normalized_first()
    bad = deepcopy(execution)
    bad["cash"] = "941"
    bad["receipt_hash"] = ""
    from finance_quant.execution.conformance import canonical_receipt_hash

    bad["receipt_hash"] = canonical_receipt_hash(bad, load_runtime_contract())
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        initial_hash = store.state_hash()
        with pytest.raises(ExecutionApplicationError, match="terminal cash mismatch"):
            commit_lean_session(
                store,
                bad,
                fixture,
                session_id="session-1",
                strategy_hash="1" * 64,
                risk_hash="2" * 64,
            )
        assert store.state_hash() == initial_hash
        assert store.session_receipts() == []


def test_fixture_binding_and_runtime_pin_fail_closed_before_account_mutation(tmp_path):
    fixture, execution = _normalized_first()
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        initial_hash = store.state_hash()
        altered_fixture = deepcopy(fixture)
        altered_fixture["events"][1]["payload"]["open"] = "99"
        with pytest.raises(ExecutionApplicationError, match="supplied fixture"):
            commit_lean_session(
                store,
                execution,
                altered_fixture,
                session_id="session-1",
                strategy_hash="1" * 64,
                risk_hash="2" * 64,
            )
        with pytest.raises(ExecutionApplicationError, match="selected LEAN pin"):
            commit_lean_session(
                store,
                execution,
                fixture,
                session_id="session-1",
                strategy_hash="1" * 64,
                risk_hash="2" * 64,
                runtime_commit="0" * 40,
            )
        assert store.state_hash() == initial_hash
        assert store.session_receipts() == []
