from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_window_two():
    assert evaluate(Rolling("sum", Field("close"), 2), [{"close": 1.0}, {"close": 4.0}]) == 5.0
