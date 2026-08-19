from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Unary


def test_abs_of_positive_is_identity():
    assert evaluate(Unary("abs", Field("close")), [{"close": 7.0}]) == 7.0
