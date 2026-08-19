"""Cost-sensitivity: a strategy that only works at zero fees must be reported as such."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostScenario:
    name: str
    fee_bps: float
    slippage_bps: float


SCENARIOS = (
    CostScenario("c-free", 0.0, 0.0),
    CostScenario("c-stress2x", 10.0, 20.0),
)


def net_return(gross: float, turnover: float, scenario: CostScenario) -> float:
    cost = turnover * (scenario.fee_bps + scenario.slippage_bps) / 10_000.0
    return gross - cost


def only_works_at_zero_fees(gross: float, turnover: float) -> bool:
    free = net_return(gross, turnover, SCENARIOS[0])
    stressed = net_return(gross, turnover, SCENARIOS[1])
    return free > 0 and stressed <= 0
