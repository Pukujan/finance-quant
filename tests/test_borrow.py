import pytest

from finance_quant.execution.borrow import BorrowUnavailable, DEFAULT, DEBUG_INFINITE_ZERO, assert_short_allowed


def test_default_borrow_model_rejects_shorts():
    assert_short_allowed(DEBUG_INFINITE_ZERO, "sell")
    with pytest.raises(BorrowUnavailable):
        assert_short_allowed(DEFAULT, "sell")
    assert_short_allowed(DEFAULT, "buy")
