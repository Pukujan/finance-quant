from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, RollingPair
import pytest


def test_rolling_pair_window_one_is_rejected():
    with pytest.raises(TemporalError):
        check(RollingPair("corr", Field("close"), Field("volume"), 1))
    assert check(RollingPair("corr", Field("close"), Field("volume"), 2)).min_lookback_bars == 1
