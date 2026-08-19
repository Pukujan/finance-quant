from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_rank_window_one_is_one():
    assert evaluate(Rolling("rank", Field("close"), 1), [{"close": 5.0}]) == 1.0
