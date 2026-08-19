from finance_quant.acceptance.contamination import contamination_flag


def test_holdout_honey_case_flags_suspicious_sealed_outperformance():
    assert contamination_flag(0.01, 0.9)
    assert not contamination_flag(0.2, 0.21)
