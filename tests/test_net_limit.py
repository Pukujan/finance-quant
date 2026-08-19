from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto
import pytest


def test_net_limit_vetoes_large_one_sided_buy():
    state = PortfolioState(gross_exposure=0.0, net_exposure=0.49, loss=0.0)
    with pytest.raises(RiskVeto, match="net"):
        veto(state, OrderIntent(0.1, "buy"), RiskLimits(max_net=0.5, max_gross=2.0))
