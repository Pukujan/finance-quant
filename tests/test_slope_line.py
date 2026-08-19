from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_slope_of_perfect_line_volume_on_close():
    expr = RollingPair("slope", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 2.0}, {"close": 2.0, "volume": 4.0}, {"close": 3.0, "volume": 6.0}]
    assert abs(evaluate(expr, hist) - 2.0) < 1e-9
