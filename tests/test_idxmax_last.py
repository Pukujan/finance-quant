from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmax_of_increasing_series_is_last_index():
    expr = Rolling("idxmax", Field("close"), 3)
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 3.0}]
    assert evaluate(expr, hist) == 2.0
