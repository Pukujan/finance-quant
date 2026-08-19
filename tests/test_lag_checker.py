import pytest

from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, Lag


def test_negative_lag_is_rejected():
    expr = Lag(Field("close"), -1)
    with pytest.raises(TemporalError, match="negative lag"):
        check(expr)


def test_positive_lag_increases_lookback():
    expr = Lag(Field("close"), 3)
    cert = check(expr)
    assert cert.max_lookahead_days == 0
    assert cert.min_lookback_bars == 3
