from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, RollingPair
import pytest


def test_rolling_pair_zero_window_rejected():
    with pytest.raises(TemporalError):
        check(RollingPair("cov", Field("close"), Field("volume"), 0))
