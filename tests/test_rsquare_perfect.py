from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_rsquare_is_one_on_perfect_line():
    expr = RollingPair("rsquare", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 2.0}, {"close": 2.0, "volume": 4.0}, {"close": 3.0, "volume": 6.0}]
    assert abs(evaluate(expr, hist) - 1.0) < 1e-9
