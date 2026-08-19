from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_rank_window_two_last_is_one_when_highest():
    expr = Rolling("rank", Field("close"), 2)
    hist = [{"close": 1.0}, {"close": 3.0}]
    assert evaluate(expr, hist) == 1.0
