import random

import pytest

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


def test_spearman_p_matches_t_distribution_reference():
    scipy = pytest.importorskip("scipy.stats")
    t_stat = (8 / 3) ** 0.5
    assert spearman_p_approx(0.5, 10) == pytest.approx(2 * scipy.t.sf(t_stat, 8))


def test_spearman_p_is_approximately_uniform_under_null():
    pytest.importorskip("scipy.stats")
    rng = random.Random(20260821)
    n = 20
    x = list(range(n))
    pvalues = []
    for _ in range(1000):
        y = x.copy()
        rng.shuffle(y)
        x_mean = y_mean = (n - 1) / 2
        numerator = sum((x_i - x_mean) * (y_i - y_mean) for x_i, y_i in zip(x, y))
        denominator = sum((value - x_mean) ** 2 for value in x)
        rho = numerator / denominator
        pvalues.append(spearman_p_approx(rho, n))

    rejection_rate = sum(p < 0.05 for p in pvalues) / len(pvalues)
    assert 0.02 <= rejection_rate <= 0.08
