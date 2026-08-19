from finance_quant.search.deflate import spearman_p_approx


def test_spearman_p_is_one_for_tiny_n():
    assert spearman_p_approx(1.0, 2) == 1.0
    assert 0.0 < spearman_p_approx(0.5, 10) <= 1.0
