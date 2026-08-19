from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Binary, CrossSection, Field
import pytest


def test_mixed_universe_identities_are_rejected():
    expr = Binary(
        "add",
        CrossSection("rank", Field("close"), "FIXIDX"),
        CrossSection("rank", Field("close"), "OTHER"),
    )
    with pytest.raises(TemporalError, match="universe"):
        check(expr)
