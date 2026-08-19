from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_std_window_two_positive():
    hist = [{"close": 1.0}, {"close": 3.0}]
    assert evaluate(Rolling("std", Field("close"), 2), hist) > 0
