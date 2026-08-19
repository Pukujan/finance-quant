from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_max_five():
    hist = [{"close": float(i)} for i in (1, 3, 2, 9, 4)]
    assert evaluate(Rolling("max", Field("close"), 5), hist) == 9.0
