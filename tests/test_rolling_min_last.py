from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_min_of_decreasing_series_is_last():
    expr = Rolling("min", Field("close"), 3)
    hist = [{"close": 5.0}, {"close": 3.0}, {"close": 1.0}]
    assert evaluate(expr, hist) == 1.0
