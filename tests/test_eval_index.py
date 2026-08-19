from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_mean_ignores_bars_after_index():
    expr = Rolling("mean", Field("close"), 2)
    hist = [{"close": 2.0}, {"close": 4.0}, {"close": 100.0}]
    assert evaluate(expr, hist, index=1) == 3.0
