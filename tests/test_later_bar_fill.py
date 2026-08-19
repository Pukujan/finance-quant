from finance_quant.execution.fills import FillEvent, assert_fill_legal


def test_later_bar_close_is_legal_if_not_same_bar():
    assert_fill_legal(FillEvent("2024-01-02", "2024-01-04", "close"))
