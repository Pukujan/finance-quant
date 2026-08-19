from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Binary, Field
import pytest


def test_unknown_binary_op_is_rejected():
    with pytest.raises(TemporalError):
        check(Binary("pow", Field("close"), Field("volume")))
