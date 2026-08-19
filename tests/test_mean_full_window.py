from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_window_equals_length():
    hist = [{"close": 1.0}, {"close": 3.0}, {"close": 5.0}, {"close": 7.0}]
    assert evaluate(Rolling("mean", Field("close"), 4), hist) == 4.0
