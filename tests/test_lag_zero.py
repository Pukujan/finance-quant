from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Lag


def test_lag_zero_is_identity():
    expr = Lag(Field("close"), 0)
    hist = [{"close": 5.0}, {"close": 9.0}]
    assert evaluate(expr, hist) == 9.0
