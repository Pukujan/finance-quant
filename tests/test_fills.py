import pytest

from finance_quant.execution.fills import FillContractError, FillEvent, assert_fill_legal


def test_same_bar_fill_is_a_contract_violation():
    with pytest.raises(FillContractError, match="t_plus_1"):
        assert_fill_legal(FillEvent("2024-01-02", "2024-01-02", "same_bar"))


def test_next_bar_open_is_legal():
    assert_fill_legal(FillEvent("2024-01-02", "2024-01-03", "open"))
