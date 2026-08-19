from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_of_constants():
    hist = [{"close": 2.0}] * 5
    assert evaluate(Rolling("sum", Field("close"), 5), hist) == 10.0
