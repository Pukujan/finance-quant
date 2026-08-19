from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_does_not_use_bars_before_window():
    expr = Rolling("mean", Field("close"), 2)
    hist = [{"close": 100.0}, {"close": 2.0}, {"close": 4.0}]
    assert evaluate(expr, hist) == 3.0
