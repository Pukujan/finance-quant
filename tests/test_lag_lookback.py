from finance_quant.dsl.checker import check
from finance_quant.dsl.ir import Binary, Field, Lag


def test_lag_lookback_adds_to_certificate():
    expr = Binary("sub", Field("close"), Lag(Field("close"), 4))
    assert check(expr).min_lookback_bars == 4
    assert check(expr).max_lookahead_days == 0
