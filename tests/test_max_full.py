from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_max_window_equals_length():
    hist = [{"close": 1.0}, {"close": 8.0}, {"close": 3.0}]
    assert evaluate(Rolling("max", Field("close"), 3), hist) == 8.0
