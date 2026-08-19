from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmax_window_one_is_zero():
    assert evaluate(Rolling("idxmax", Field("close"), 1), [{"close": 9.0}]) == 0.0
