from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Const, Field, Binary


def test_const_plus_field():
    hist = [{"close": 3.0}]
    assert evaluate(Binary("add", Const(1.5), Field("close")), hist) == 4.5
