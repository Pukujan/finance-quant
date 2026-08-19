from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_rolling_corr_is_zero_when_one_series_is_constant():
    expr = RollingPair("corr", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 10.0}, {"close": 1.0, "volume": 20.0}, {"close": 1.0, "volume": 30.0}]
    assert evaluate(expr, hist) == 0.0
