from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_slope_zero_when_x_is_constant():
    expr = RollingPair("slope", Field("close"), Field("volume"), 3)
    hist = [{"close": 2.0, "volume": 10.0}, {"close": 2.0, "volume": 20.0}, {"close": 2.0, "volume": 30.0}]
    assert evaluate(expr, hist) == 0.0
