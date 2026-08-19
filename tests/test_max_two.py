from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_max_window_two():
    hist = [{"close": 1.0}, {"close": 5.0}]
    assert evaluate(Rolling("max", Field("close"), 2), hist) == 5.0
