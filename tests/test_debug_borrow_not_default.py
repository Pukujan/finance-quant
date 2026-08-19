from finance_quant.execution.borrow import DEBUG_INFINITE_ZERO
from finance_quant.execution.lean import ExecutionContract


def test_infinite_zero_borrow_is_named_debug_not_default():
    assert DEBUG_INFINITE_ZERO.name.startswith("debug")
    assert ExecutionContract().short_borrow_model != DEBUG_INFINITE_ZERO.name if hasattr(ExecutionContract(), "short_borrow_model") else True
    contract = ExecutionContract()
    assert "signal_at_bar_t" in contract.daily_fill_rule
