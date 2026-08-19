from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_std_window_one_is_zero():
    assert evaluate(Rolling("std", Field("close"), 1), [{"close": 5.0}]) == 0.0
