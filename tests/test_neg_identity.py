from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Unary


def test_double_neg_is_identity():
    hist = [{"close": 5.0}]
    assert evaluate(Unary("neg", Unary("neg", Field("close"))), hist) == 5.0
