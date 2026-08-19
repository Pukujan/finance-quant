from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Const


def test_const_ignores_history():
    assert evaluate(Const(42.0), [{"close": 1.0}, {"close": 99.0}]) == 42.0
