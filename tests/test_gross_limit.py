from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto
import pytest


def test_gross_limit_vetoes_large_notional():
    state = PortfolioState(gross_exposure=0.8, net_exposure=0.0, loss=0.0)
    with pytest.raises(RiskVeto, match="gross"):
        veto(state, OrderIntent(0.3, "buy"), RiskLimits(max_gross=1.0, max_net=1.0))
