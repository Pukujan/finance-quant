from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_cov_zero_when_either_series_constant():
    expr = RollingPair("cov", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 5.0}, {"close": 2.0, "volume": 5.0}, {"close": 3.0, "volume": 5.0}]
    assert evaluate(expr, hist) == 0.0
