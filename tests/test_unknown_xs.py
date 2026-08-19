from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import CrossSection, Field
import pytest


def test_unknown_cross_section_op_is_rejected():
    with pytest.raises(TemporalError):
        check(CrossSection("softmax", Field("close"), "FIXIDX"))
