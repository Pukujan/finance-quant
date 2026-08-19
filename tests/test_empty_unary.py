from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, Unary
import pytest


def test_empty_unary_op_is_rejected():
    with pytest.raises(TemporalError):
        check(Unary("", Field("close")))
