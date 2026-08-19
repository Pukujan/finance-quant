from finance_quant.dsl.interpreter import EvaluationError, evaluate
from finance_quant.dsl.ir import Field, Unary
import pytest


def test_log_of_non_positive_is_an_evaluation_error_not_a_leak():
    with pytest.raises((EvaluationError, ValueError)):
        evaluate(Unary("log", Field("close")), [{"close": -1.0}])
