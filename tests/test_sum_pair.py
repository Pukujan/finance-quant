from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_sum_two_equals_pair_sum():
    hist = [{"close": 7.0}, {"close": 8.0}]
    assert evaluate(Rolling("sum", Field("close"), 2), hist) == 15.0
