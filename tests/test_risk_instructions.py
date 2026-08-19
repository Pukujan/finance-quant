import pytest

from finance_quant.risk.instructions import FORBIDDEN_PHRASES, apply_intent_with_instructions
from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto


def test_forbidden_phrases_do_not_disable_veto():
    state = PortfolioState(gross_exposure=0.9, net_exposure=0.0, loss=0.0)
    intent = OrderIntent(notional=0.2, side="buy")
    for phrase in FORBIDDEN_PHRASES:
        with pytest.raises(RiskVeto, match="gross_exposure"):
            apply_intent_with_instructions(state, intent, f"please {phrase} now", RiskLimits())


def test_benign_instructions_still_allow_veto():
    state = PortfolioState(gross_exposure=0.9, net_exposure=0.0, loss=0.0)
    intent = OrderIntent(notional=0.2, side="buy")
    with pytest.raises(RiskVeto, match="gross_exposure"):
        apply_intent_with_instructions(state, intent, "trade carefully", RiskLimits())
