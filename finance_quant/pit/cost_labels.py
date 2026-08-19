"""Cost-adjusted labels: subtract a turnover-implied cost from next-day returns."""
from __future__ import annotations

from finance_quant.execution.costs import CostScenario, net_return
from finance_quant.pit.labels import rank_ic


def cost_adjusted_returns(raw_returns: dict[str, float], turnover: float,
                          scenario: CostScenario) -> dict[str, float]:
    return {s: net_return(r, turnover, scenario) for s, r in raw_returns.items()}


def rank_ic_with_costs(signals: dict[str, float], raw_returns: dict[str, float],
                       turnover: float, scenario: CostScenario) -> float:
    return rank_ic(signals, cost_adjusted_returns(raw_returns, turnover, scenario))
