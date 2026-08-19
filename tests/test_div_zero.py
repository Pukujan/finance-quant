from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Binary, Const, Field
import pytest


def test_literal_division_by_zero_is_rejected_statically():
    with pytest.raises(TemporalError, match="zero"):
        check(Binary("div", Field("close"), Const(0)))
    assert check(Binary("div", Field("close"), Const(2))).max_lookahead_days == 0
