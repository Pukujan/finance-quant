from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_rank_lowest_is_positive():
    expr = Rolling("rank", Field("close"), 3)
    hist = [{"close": 9.0}, {"close": 8.0}, {"close": 1.0}]
    r = evaluate(expr, hist)
    assert 0.0 < r <= 1.0
    assert r <= evaluate(Rolling("rank", Field("close"), 3), [{"close": 1.0}, {"close": 2.0}, {"close": 9.0}])
