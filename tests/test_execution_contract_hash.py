from finance_quant.execution.lean import ExecutionContract


def test_execution_contract_hash_changes_when_fill_model_changes():
    a = ExecutionContract()
    b = ExecutionContract(fill_model="ImmediateFillModel")
    assert a.hash != b.hash
    assert a.daily_fill_rule.startswith("signal_at_bar_t")
