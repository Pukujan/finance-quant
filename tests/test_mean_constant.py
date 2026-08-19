from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_constant_series():
    expr = Rolling("mean", Field("close"), 4)
    hist = [{"close": 3.0}] * 4
    assert evaluate(expr, hist) == 3.0
