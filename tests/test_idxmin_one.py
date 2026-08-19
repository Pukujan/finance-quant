from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_idxmin_window_one_is_zero():
    assert evaluate(Rolling("idxmin", Field("close"), 1), [{"close": 2.0}]) == 0.0
