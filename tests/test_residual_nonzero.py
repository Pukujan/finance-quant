from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair


def test_residual_nonzero_when_not_colinear():
    expr = RollingPair("residual", Field("close"), Field("volume"), 3)
    hist = [{"close": 1.0, "volume": 10.0}, {"close": 2.0, "volume": 11.0}, {"close": 3.0, "volume": 100.0}]
    assert abs(evaluate(expr, hist)) > 1e-6
