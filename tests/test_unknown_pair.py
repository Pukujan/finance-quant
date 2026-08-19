from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, RollingPair
import pytest


def test_unknown_rolling_pair_op_is_rejected():
    with pytest.raises(TemporalError):
        check(RollingPair("beta", Field("close"), Field("volume"), 5))
