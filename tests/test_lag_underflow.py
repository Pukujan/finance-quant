from finance_quant.dsl.interpreter import EvaluationError, evaluate
from finance_quant.dsl.ir import Field, Lag
import pytest


def test_lag_beyond_history_is_evaluation_error_not_a_future_read():
    with pytest.raises(EvaluationError):
        evaluate(Lag(Field("close"), 5), [{"close": 1.0}])
