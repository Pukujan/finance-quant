from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_std_positive_on_spread_series():
    expr = Rolling("std", Field("close"), 3)
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 3.0}]
    assert evaluate(expr, hist) > 0
