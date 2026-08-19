from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmin_of_decreasing_series_is_last_index():
    expr = Rolling("idxmin", Field("close"), 3)
    hist = [{"close": 3.0}, {"close": 2.0}, {"close": 1.0}]
    assert evaluate(expr, hist) == 2.0
