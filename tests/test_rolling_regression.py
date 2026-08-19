from finance_quant.dsl.checker import check
from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair
from finance_quant.dsl.qlib import compile_expr


def test_rolling_slope_and_rsquare_are_historical():
    expr = RollingPair("slope", Field("close"), Field("volume"), 3)
    assert check(expr).max_lookahead_days == 0
    hist = [{"close": 1.0, "volume": 10.0}, {"close": 2.0, "volume": 20.0}, {"close": 3.0, "volume": 30.0}]
    assert abs(evaluate(expr, hist) - 10.0) < 1e-9
    r2 = RollingPair("rsquare", Field("close"), Field("volume"), 3)
    assert abs(evaluate(r2, hist) - 1.0) < 1e-9
    assert compile_expr(expr) == "Slope($close,$volume,3)"
