from finance_quant.search.overfit import search_artifact


def test_search_artifact_true_when_best_near_median():
    scores = [0.01, 0.02, 0.015, 0.018, 0.022]
    assert search_artifact(scores, deflated_threshold=0.05)


def test_search_artifact_false_when_best_is_outlier():
    scores = [0.01, 0.02, 0.015, 0.018, 0.50]
    assert not search_artifact(scores, deflated_threshold=0.05)
