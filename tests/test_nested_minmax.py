from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Const, Field


def test_nested_min_of_max():
    hist = [{"close": 3.0}]
    expr = Binary("min", Binary("max", Field("close"), Const(1.0)), Const(2.0))
    assert evaluate(expr, hist) == 2.0
