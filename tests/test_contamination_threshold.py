from finance_quant.acceptance.contamination import contamination_flag


def test_contamination_threshold_is_exclusive():
    assert not contamination_flag(0.1, 0.6, threshold=0.5)
    assert contamination_flag(0.1, 0.61, threshold=0.5)
