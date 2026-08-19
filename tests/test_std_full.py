from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_std_window_equals_length_positive():
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 3.0}, {"close": 4.0}]
    assert evaluate(Rolling("std", Field("close"), 4), hist) > 0
