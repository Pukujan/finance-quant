from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_min_full_window():
    hist = [{"close": 4.0}, {"close": 1.0}, {"close": 3.0}]
    assert evaluate(Rolling("min", Field("close"), 3), hist) == 1.0
