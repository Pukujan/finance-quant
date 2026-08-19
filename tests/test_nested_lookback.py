from finance_quant.dsl.checker import check
from finance_quant.dsl.ir import Field, Lag, Rolling


def test_nested_lag_and_rolling_lookback_adds():
    expr = Rolling("mean", Lag(Field("close"), 2), 5)
    cert = check(expr)
    assert cert.min_lookback_bars == 2 + 4
    assert cert.max_lookahead_days == 0
