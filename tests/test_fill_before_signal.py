from finance_quant.execution.fills import FillContractError, FillEvent, assert_fill_legal
import pytest


def test_fill_before_signal_is_impossible():
    with pytest.raises(FillContractError, match="before signal"):
        assert_fill_legal(FillEvent("2024-01-04", "2024-01-03", "open"))
