from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_rolling_cov_positive_on_aligned_series():
    expr = RollingPair("cov", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 10.0}, {"close": 2.0, "volume": 20.0}, {"close": 3.0, "volume": 30.0}]
    assert evaluate(expr, hist) > 0
