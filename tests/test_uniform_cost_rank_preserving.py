from finance_quant.execution.costs import SCENARIOS
from finance_quant.pit.cost_labels import rank_ic_with_costs
from finance_quant.pit.labels import rank_ic


def test_uniform_turnover_cost_does_not_change_cross_sectional_rank_ic():
    signals = {"AAA": 3.0, "BBB": 1.0, "CCC": 2.0}
    rets = {"AAA": 0.05, "BBB": -0.01, "CCC": 0.02}
    raw = rank_ic(signals, rets)
    stressed = rank_ic_with_costs(signals, rets, 1.0, SCENARIOS[1])
    assert raw == stressed
