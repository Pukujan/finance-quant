from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_three_simple():
    expr = Rolling("mean", Field("close"), 3)
    hist = [{"close": 2.0}, {"close": 4.0}, {"close": 6.0}]
    assert evaluate(expr, hist) == 4.0
