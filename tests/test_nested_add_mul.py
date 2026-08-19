from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Const, Field


def test_nested_add_mul():
    hist = [{"close": 2.0}]
    expr = Binary("add", Binary("mul", Field("close"), Const(3.0)), Const(1.0))
    assert evaluate(expr, hist) == 7.0
