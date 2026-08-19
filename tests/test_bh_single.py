from finance_quant.search.deflate import benjamini_hochberg


def test_bh_single_borderline():
    assert benjamini_hochberg([0.04], alpha=0.05) == [True]
    assert benjamini_hochberg([0.06], alpha=0.05) == [False]
