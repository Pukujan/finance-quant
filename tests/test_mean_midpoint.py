from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_two_equals_midpoint():
    hist = [{"close": 10.0}, {"close": 20.0}]
    assert evaluate(Rolling("mean", Field("close"), 2), hist) == 15.0
