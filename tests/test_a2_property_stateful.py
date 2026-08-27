from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path

from hypothesis import given, settings, strategies as st

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits
from finance_quant.trader.account import VirtualAccountStore
from finance_quant.trader.risk import gate_order_intent


@given(
    parts=st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=6),
    side=st.sampled_from(["BUY", "SELL"]),
    price=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=60, deadline=None)
def test_fq_prop_024_028_stateful_fill_sequences_reconcile(parts, side, price):
    quantity = sum(parts)
    initial_cash = Decimal("100000")
    signed = Decimal(quantity if side == "BUY" else -quantity)
    expected_cash = initial_cash - signed * Decimal(price)
    with tempfile.TemporaryDirectory() as tmp:
        with VirtualAccountStore(Path(tmp) / "account.db", initial_cash=str(initial_cash)) as store:
            assert store.submit_order(
                order_id="order-1",
                intent_id="intent-1",
                session_id="session-1",
                instrument_id="AAA",
                side=side,
                quantity=str(quantity),
                created_at="2026-06-01T20:00:00Z",
            )
            for index, part in enumerate(parts):
                kwargs = {
                    "fill_id": f"fill-{index}",
                    "order_id": "order-1",
                    "session_id": "session-1",
                    "instrument_id": "AAA",
                    "quantity": str(part),
                    "price": str(price),
                    "fee": "0",
                    "event_time": f"2026-06-02T13:{30 + index:02d}:00Z",
                    "source_event_id": f"event-{index}",
                }
                assert store.apply_fill(**kwargs) is True
                after = store.state_hash()
                assert store.apply_fill(**kwargs) is False
                assert store.state_hash() == after
            state = store.authoritative_state()
            assert Decimal(state["cash"]) == expected_cash
            assert Decimal(state["positions"][0]["quantity"]) == signed
            assert state["orders"][0]["filled_quantity"] == str(quantity)
            assert state["orders"][0]["state"] == "FILLED"
            assert len(state["fills"]) == len(parts)
            assert len(state["cash_ledger"]) == len(parts)


@given(
    gross=st.floats(min_value=0.0, max_value=1.5, allow_nan=False, allow_infinity=False),
    net=st.floats(min_value=-0.8, max_value=0.8, allow_nan=False, allow_infinity=False),
    loss=st.floats(min_value=0.0, max_value=0.2, allow_nan=False, allow_infinity=False),
    notional=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    side=st.sampled_from(["buy", "sell"]),
)
@settings(max_examples=100, deadline=None)
def test_fq_prop_027_property_risk_gate_never_widens(gross, net, loss, notional, side):
    decision = gate_order_intent(
        PortfolioState(gross_exposure=gross, net_exposure=net, loss=loss),
        OrderIntent(notional=notional, side=side),
        RiskLimits(max_gross=1.0, max_net=0.5, max_loss=0.1),
    )
    assert 0.0 <= decision.approved_notional <= decision.requested_notional
    assert decision.approved_notional in {0.0, decision.requested_notional}
