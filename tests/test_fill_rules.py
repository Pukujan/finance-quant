import pytest

from finance_quant.execution.fills import FillContractError, FillEvent, assert_fill_legal
from finance_quant.execution.lean import ExecutionContract


def test_same_bar_fill_is_illegal():
    event = FillEvent(signal_bar="2024-01-02", fill_bar="2024-01-02", fill_time="same_bar")
    with pytest.raises(FillContractError, match="signal_at_bar_t"):
        assert_fill_legal(event, ExecutionContract())


def test_next_open_fill_is_legal():
    event = FillEvent(signal_bar="2024-01-02", fill_bar="2024-01-03", fill_time="open")
    assert_fill_legal(event, ExecutionContract()) is None


def test_fill_before_signal_is_illegal():
    event = FillEvent(signal_bar="2024-01-03", fill_bar="2024-01-02", fill_time="open")
    with pytest.raises(FillContractError, match="fill before signal"):
        assert_fill_legal(event, ExecutionContract())
