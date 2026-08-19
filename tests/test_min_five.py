from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_min_five():
    hist = [{"close": float(i)} for i in (5, 2, 8, 1, 4)]
    assert evaluate(Rolling("min", Field("close"), 5), hist) == 1.0
