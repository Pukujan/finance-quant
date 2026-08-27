from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits
from finance_quant.trader.risk import gate_order_intent


@given(
    notional=st.floats(min_value=0, max_value=2, allow_nan=False, allow_infinity=False),
    side=st.sampled_from(["buy", "sell"]),
)
def test_fq_prop_027_risk_gate_never_widens(notional, side):
    decision = gate_order_intent(
        PortfolioState(gross_exposure=0.0, net_exposure=0.0, loss=0.0),
        OrderIntent(notional=notional, side=side),
        RiskLimits(max_gross=1.0, max_net=0.5, max_loss=0.1),
    )
    assert 0.0 <= decision.approved_notional <= decision.requested_notional + 1e-12
    if decision.status == "APPROVED":
        assert decision.approved_notional == decision.requested_notional
    else:
        assert decision.status == "REJECTED"
        assert decision.approved_notional == 0.0


def test_invalid_side_and_negative_notional_fail_closed():
    state = PortfolioState(gross_exposure=0.0, net_exposure=0.0, loss=0.0)
    with pytest.raises(ValueError, match="side"):
        gate_order_intent(state, OrderIntent(notional=0.1, side="hold"))
    with pytest.raises(ValueError, match="notional"):
        gate_order_intent(state, OrderIntent(notional=-0.1, side="buy"))
