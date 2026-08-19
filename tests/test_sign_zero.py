from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Unary


def test_sign_of_zero_is_zero():
    assert evaluate(Unary("sign", Field("close")), [{"close": 0.0}]) == 0.0
    assert evaluate(Unary("sign", Field("close")), [{"close": 2.0}]) == 1.0
