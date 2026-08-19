from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_five():
    hist = [{"close": 1.0}] * 5
    assert evaluate(Rolling("sum", Field("close"), 5), hist) == 5.0
