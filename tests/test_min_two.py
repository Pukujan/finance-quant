from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_min_window_two():
    hist = [{"close": 8.0}, {"close": 3.0}]
    assert evaluate(Rolling("min", Field("close"), 2), hist) == 3.0
