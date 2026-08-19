from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_quantile_window_one_is_identity():
    assert evaluate(Rolling("quantile", Field("close"), 1), [{"close": 6.0}]) == 6.0
