from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_quantile_of_sorted_window_is_middle():
    expr = Rolling("quantile", Field("close"), 3)
    hist = [{"close": 10.0}, {"close": 20.0}, {"close": 30.0}]
    assert evaluate(expr, hist) == 20.0
