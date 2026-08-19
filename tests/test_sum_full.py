from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_window_equals_length():
    hist = [{"close": 1.0}, {"close": 2.0}, {"close": 3.0}, {"close": 4.0}]
    assert evaluate(Rolling("sum", Field("close"), 4), hist) == 10.0
