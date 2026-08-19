from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_max_window_one_is_identity():
    assert evaluate(Rolling("max", Field("close"), 1), [{"close": 8.0}]) == 8.0
