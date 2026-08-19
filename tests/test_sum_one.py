from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_window_one_is_identity():
    assert evaluate(Rolling("sum", Field("close"), 1), [{"close": 9.0}]) == 9.0
