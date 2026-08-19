from finance_quant.execution.costs import only_works_at_zero_fees


def test_zero_fee_only_detector():
    # free > 0 and stressed <= 0
    assert only_works_at_zero_fees(0.005, 2.5)
    assert not only_works_at_zero_fees(0.20, 1.0)
    assert not only_works_at_zero_fees(-0.05, 0.5)
