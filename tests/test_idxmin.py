from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmin_picks_first_minimum():
    expr = Rolling("idxmin", Field("close"), 3)
    hist = [{"close": 2.0}, {"close": 1.0}, {"close": 1.0}]
    assert evaluate(expr, hist) == 1.0
