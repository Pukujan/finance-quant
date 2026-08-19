from finance_quant.search.deflate import benjamini_hochberg


def test_bh_empty_returns_empty():
    assert benjamini_hochberg([], 0.05) == []


def test_bh_all_null_accepts_none():
    pvals = [0.5, 0.6, 0.7, 0.8]
    assert not any(benjamini_hochberg(pvals, 0.05))


def test_bh_strong_signal_accepted():
    pvals = [0.001, 0.5, 0.6, 0.7]
    mask = benjamini_hochberg(pvals, 0.05)
    assert mask[0]
    assert not any(mask[1:])
