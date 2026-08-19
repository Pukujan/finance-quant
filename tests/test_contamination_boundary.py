from finance_quant.acceptance.contamination import contamination_flag


def test_contamination_flag_boundary():
    assert contamination_flag(0.1, 0.61, threshold=0.5)
    assert not contamination_flag(0.1, 0.6, threshold=0.5)


def test_contamination_flag_negative_delta():
    assert not contamination_flag(0.6, 0.1, threshold=0.5)
