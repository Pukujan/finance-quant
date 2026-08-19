"""Cost-scenario evaluation as an explicit WorkOrder-shaped job, not a hidden default."""
from __future__ import annotations

from finance_quant.execution.costs import SCENARIOS, net_return


def evaluate_cost_scenarios(gross: float, turnover: float) -> dict[str, float]:
    return {s.name: net_return(gross, turnover, s) for s in SCENARIOS}
