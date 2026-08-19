from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto
import pytest


def test_loss_limit_vetoes_even_small_orders():
    state = PortfolioState(gross_exposure=0.1, net_exposure=0.0, loss=0.2)
    with pytest.raises(RiskVeto, match="loss"):
        veto(state, OrderIntent(0.01, "buy"), RiskLimits(max_loss=0.1))
