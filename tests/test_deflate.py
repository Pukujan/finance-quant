from finance_quant.search.deflate import benjamini_hochberg, spearman_p_approx


def test_bh_accepts_nothing_when_all_p_large():
    assert benjamini_hochberg([0.9, 0.8, 0.7], alpha=0.05) == [False, False, False]


def test_bh_accepts_very_small_p():
    mask = benjamini_hochberg([1e-8, 0.9, 0.8], alpha=0.05)
    assert mask[0] is True
    assert mask[1] is False


def test_spearman_p_decreases_with_abs_ic():
    assert spearman_p_approx(0.9, 20) < spearman_p_approx(0.1, 20)
    assert spearman_p_approx(0.0, 2) == 1.0
