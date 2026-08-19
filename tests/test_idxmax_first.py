from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmax_picks_first_maximum():
    expr = Rolling("idxmax", Field("close"), 3)
    hist = [{"close": 3.0}, {"close": 3.0}, {"close": 1.0}]
    assert evaluate(expr, hist) == 0.0
