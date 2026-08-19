import pytest

from finance_quant.pit.cost_labels import cost_adjusted_returns, rank_ic_with_costs
from finance_quant.execution.costs import SCENARIOS


def test_cost_adjusted_returns_reduce_with_stress():
    raw = {"A": 0.10, "B": 0.05}
    free = cost_adjusted_returns(raw, 1.0, SCENARIOS[0])
    stressed = cost_adjusted_returns(raw, 1.0, SCENARIOS[1])
    assert all(stressed[s] < free[s] for s in raw)


def test_rank_ic_with_costs_invariant_to_signal_shift():
    raw = {"A": 0.10, "B": 0.05, "C": -0.02}
    signals = {"A": 1.0, "B": 2.0, "C": 0.0}
    shifted = {s: v + 10.0 for s, v in signals.items()}
    ic = rank_ic_with_costs(signals, raw, 0.5, SCENARIOS[0])
    ic_shifted = rank_ic_with_costs(shifted, raw, 0.5, SCENARIOS[0])
    assert ic == pytest.approx(ic_shifted)
