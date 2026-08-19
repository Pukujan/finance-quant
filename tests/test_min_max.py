from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Const, Field


def test_min_max_binary_ops():
    hist = [{"close": 3.0}]
    assert evaluate(Binary("min", Field("close"), Const(5.0)), hist) == 3.0
    assert evaluate(Binary("max", Field("close"), Const(5.0)), hist) == 5.0
