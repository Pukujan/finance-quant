from finance_quant.orchestration.authority import CapabilityClass, worker_environment
from finance_quant.risk.veto import OrderIntent, PortfolioState, RiskLimits, RiskVeto, veto
import pytest


def test_worker_env_has_no_risk_mutation_handles():
    env = worker_environment(CapabilityClass.RESEARCH_WORKER, base={"PATH": "x", "FQ_PROMOTION_API": "evil"})
    assert "FQ_PROMOTION_API" not in env
    assert "FQ_SEALED_STORE" not in env


def test_risk_limits_are_not_widened_by_intent_size():
    with pytest.raises(RiskVeto):
        veto(PortfolioState(0.0, 0.0, 0.0), OrderIntent(10.0, "buy"), RiskLimits(max_gross=1.0))
