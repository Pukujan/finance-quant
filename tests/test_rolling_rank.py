from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_rank_of_last_value_is_between_zero_and_one():
    expr = Rolling("rank", Field("close"), 4)
    hist = [{"close": x} for x in (1.0, 4.0, 2.0, 3.0)]
    r = evaluate(expr, hist)
    assert 0.0 < r <= 1.0
