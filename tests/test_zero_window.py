from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, Rolling
import pytest


def test_zero_window_rolling_is_rejected():
    with pytest.raises(TemporalError):
        check(Rolling("mean", Field("close"), 0))
    with pytest.raises(TemporalError):
        check(Rolling("mean", Field("close"), -3))
