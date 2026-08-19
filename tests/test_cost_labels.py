from finance_quant.execution.costs import SCENARIOS
from finance_quant.pit.cost_labels import cost_adjusted_returns, rank_ic_with_costs


def test_cost_adjusted_returns_are_worse_under_stress():
    raw = {"AAA": 0.01, "BBB": -0.01}
    free = cost_adjusted_returns(raw, 1.0, SCENARIOS[0])
    stressed = cost_adjusted_returns(raw, 1.0, SCENARIOS[1])
    assert free["AAA"] > stressed["AAA"]


def test_rank_ic_with_costs_is_bounded():
    signals = {"AAA": 1.0, "BBB": 2.0}
    rets = {"AAA": 0.02, "BBB": 0.01}
    ic = rank_ic_with_costs(signals, rets, 0.5, SCENARIOS[1])
    assert -1.0 <= ic <= 1.0
