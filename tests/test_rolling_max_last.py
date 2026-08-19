from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_max_of_increasing_series_is_last():
    expr = Rolling("max", Field("close"), 3)
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 4.0}]
    assert evaluate(expr, hist) == 4.0
