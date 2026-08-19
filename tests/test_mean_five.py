from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_five():
    hist = [{"close": float(i)} for i in range(1, 6)]
    assert evaluate(Rolling("mean", Field("close"), 5), hist) == 3.0
