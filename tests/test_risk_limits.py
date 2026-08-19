import pytest

from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto


def test_net_exposure_veto():
    state = PortfolioState(gross_exposure=0.0, net_exposure=0.45, loss=0.0)
    intent = OrderIntent(notional=0.1, side="buy")
    with pytest.raises(RiskVeto, match="net_exposure"):
        veto(state, intent, RiskLimits())


def test_loss_limit_veto():
    state = PortfolioState(gross_exposure=0.0, net_exposure=0.0, loss=0.11)
    intent = OrderIntent(notional=0.01, side="buy")
    with pytest.raises(RiskVeto, match="loss_limit"):
        veto(state, intent, RiskLimits())


def test_exactly_at_limits_passes():
    state = PortfolioState(gross_exposure=1.0, net_exposure=0.5, loss=0.1)
    intent = OrderIntent(notional=0.0, side="buy")
    veto(state, intent, RiskLimits())
