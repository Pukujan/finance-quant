from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_std_zero_on_constant_series():
    expr = Rolling("std", Field("close"), 3)
    hist = [{"close": 2.0}, {"close": 2.0}, {"close": 2.0}]
    assert evaluate(expr, hist) == 0.0
