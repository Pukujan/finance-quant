from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import CrossSection, Field
import pytest


def test_cross_section_requires_universe_name():
    with pytest.raises(TemporalError):
        check(CrossSection("rank", Field("close"), ""))
