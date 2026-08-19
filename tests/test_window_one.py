from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_window_one_is_identity():
    expr = Rolling("mean", Field("close"), 1)
    assert evaluate(expr, [{"close": 7.0}]) == 7.0
    assert evaluate(Rolling("sum", Field("close"), 1), [{"close": 7.0}]) == 7.0
