from __future__ import annotations

import pytest

from finance_quant.trader.account import AccountInvariantError, VirtualAccountStore


def _submit(store: VirtualAccountStore, *, quantity: str = "5") -> None:
    assert store.submit_order(
        order_id="order-1",
        intent_id="intent-1",
        session_id="session-1",
        instrument_id="AAA",
        side="BUY",
        quantity=quantity,
        created_at="2026-06-01T20:00:00Z",
    )


def _fill(store: VirtualAccountStore, *, fill_id: str = "fill-1", quantity: str = "2", price: str = "10", fee: str = "1") -> bool:
    return store.apply_fill(
        fill_id=fill_id,
        order_id="order-1",
        session_id="session-1",
        instrument_id="AAA",
        quantity=quantity,
        price=price,
        fee=fee,
        event_time="2026-06-02T13:30:00Z",
        source_event_id="bar-2",
    )


def test_fq_prop_023_nav_reconciles_exactly(tmp_path):
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="1000") as store:
        _submit(store)
        assert _fill(store)
        assert store.apply_fill(
            fill_id="fill-2",
            order_id="order-1",
            session_id="session-1",
            instrument_id="AAA",
            quantity="3",
            price="11",
            fee="1",
            event_time="2026-06-02T13:31:00Z",
            source_event_id="bar-2b",
        )
        nav = store.nav({"AAA": "12"})
        assert nav == {"cash": "945", "marked_position_value": "60", "nav": "1005"}


def test_fq_prop_024_fill_requires_order_and_cannot_overfill(tmp_path):
    with VirtualAccountStore(tmp_path / "missing.db", initial_cash="100") as store:
        with pytest.raises(AccountInvariantError, match="preceding order"):
            store.apply_fill(
                fill_id="orphan",
                order_id="missing",
                session_id="s",
                instrument_id="AAA",
                quantity="1",
                price="10",
                fee="0",
                event_time="t",
                source_event_id="e",
            )

    with VirtualAccountStore(tmp_path / "overfill.db", initial_cash="100") as store:
        _submit(store, quantity="1")
        before = store.state_hash()
        with pytest.raises(AccountInvariantError, match="exceeds"):
            _fill(store, quantity="2")
        assert store.state_hash() == before
        assert store.authoritative_state()["fills"] == []


def test_fq_prop_028_duplicate_fill_is_idempotent_and_reopen_is_stable(tmp_path):
    path = tmp_path / "account.db"
    with VirtualAccountStore(path, initial_cash="1000") as store:
        _submit(store)
        assert _fill(store) is True
        after_first = store.state_hash()
        assert _fill(store) is False
        assert store.state_hash() == after_first
        with pytest.raises(AccountInvariantError, match="conflicting duplicate fill_id"):
            _fill(store, quantity="1")
        assert store.state_hash() == after_first

    with VirtualAccountStore(path) as reopened:
        assert reopened.state_hash() == after_first
        state = reopened.authoritative_state()
        assert state["cash"] == "979"
        assert state["positions"] == [{"instrument_id": "AAA", "quantity": "2"}]
        assert len(state["fills"]) == 1
        assert len(state["cash_ledger"]) == 1


def test_missing_mark_for_nonzero_position_fails_closed(tmp_path):
    with VirtualAccountStore(tmp_path / "account.db", initial_cash="100") as store:
        _submit(store, quantity="1")
        _fill(store, quantity="1", price="10", fee="0")
        with pytest.raises(AccountInvariantError, match="missing mark"):
            store.nav({})


def test_existing_account_cannot_be_silently_reset(tmp_path):
    path = tmp_path / "account.db"
    with VirtualAccountStore(path, initial_cash="100"):
        pass
    with pytest.raises(AccountInvariantError, match="cannot reset"):
        VirtualAccountStore(path, initial_cash="101")
