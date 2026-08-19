from finance_quant.search.deflate import benjamini_hochberg


def test_bh_empty_and_all_tiny():
    assert benjamini_hochberg([]) == []
    assert all(benjamini_hochberg([1e-12, 1e-12, 1e-12], alpha=0.05))
