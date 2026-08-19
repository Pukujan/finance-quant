from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Unary
import math


def test_log_of_one_is_zero():
    assert abs(evaluate(Unary("log", Field("close")), [{"close": 1.0}])) < 1e-12
    assert abs(evaluate(Unary("log", Field("close")), [{"close": math.e}]) - 1.0) < 1e-9
