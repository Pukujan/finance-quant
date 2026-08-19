from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_min_window_one_is_identity():
    assert evaluate(Rolling("min", Field("close"), 1), [{"close": 4.5}]) == 4.5
