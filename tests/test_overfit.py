from finance_quant.search.overfit import search_artifact


def test_parameter_search_best_of_is_flagged_when_not_deflated():
    assert search_artifact([0.01] * 199 + [0.011])
    assert not search_artifact([0.01] * 100 + [0.4])
