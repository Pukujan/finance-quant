from finance_quant.execution.costs import only_works_at_zero_fees, net_return, SCENARIOS


def test_zero_fee_only_strategy_is_flagged():
    assert only_works_at_zero_fees(0.001, 2.0)
    assert not only_works_at_zero_fees(0.5, 0.01)
    assert net_return(0.1, 1.0, SCENARIOS[0]) > net_return(0.1, 1.0, SCENARIOS[1])
