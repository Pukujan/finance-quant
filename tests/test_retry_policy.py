from finance_quant.orchestration.retries import RetryPolicy
from finance_quant.orchestration.contracts import TerminalStatus


def test_retry_policy_only_retries_failed_and_crashed():
    p = RetryPolicy(max_retries=2)
    assert p.should_retry(TerminalStatus.FAILED, 0)
    assert p.should_retry(TerminalStatus.CRASHED, 1)
    assert not p.should_retry(TerminalStatus.COMPLETED, 0)
    assert not p.should_retry(TerminalStatus.FAILED, 2)
    assert not p.should_retry(TerminalStatus.CANCELLED, 0)
