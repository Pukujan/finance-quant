from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_window_five_midpoint():
    hist = [{"close": 2.0}, {"close": 4.0}, {"close": 6.0}, {"close": 8.0}, {"close": 10.0}]
    assert evaluate(Rolling("mean", Field("close"), 5), hist) == 6.0
