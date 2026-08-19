from finance_quant.dsl.checker import check
from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling
from finance_quant.dsl.qlib import compile_expr


def test_idxmax_idxmin_are_historical():
    expr = Rolling("idxmax", Field("close"), 3)
    assert check(expr).max_lookahead_days == 0
    hist = [{"close": 1.0}, {"close": 3.0}, {"close": 2.0}]
    assert evaluate(expr, hist) == 1.0
    assert compile_expr(Rolling("idxmin", Field("close"), 3)) == "IdxMin($close,3)"
