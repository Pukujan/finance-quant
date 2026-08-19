from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_rank_highest_is_one():
    expr = Rolling("rank", Field("close"), 3)
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 5.0}]
    assert evaluate(expr, hist) == 1.0
