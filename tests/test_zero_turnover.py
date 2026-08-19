from finance_quant.execution.costs import CostScenario, net_return


def test_zero_turnover_means_net_equals_gross():
    s = CostScenario("x", 50.0, 50.0)
    assert net_return(0.12, 0.0, s) == 0.12
