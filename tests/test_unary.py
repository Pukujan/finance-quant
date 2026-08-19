from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Unary


def test_sign_and_abs_are_historical():
    hist = [{"close": -4.0}]
    assert evaluate(Unary("abs", Field("close")), hist) == 4.0
    assert evaluate(Unary("sign", Field("close")), hist) == -1.0
    assert evaluate(Unary("neg", Field("close")), hist) == 4.0
