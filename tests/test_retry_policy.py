from finance_quant.orchestration.contracts import TerminalStatus
from finance_quant.orchestration.retries import RetryPolicy


def test_retry_on_crashed():
    policy = RetryPolicy()
    assert policy.should_retry(TerminalStatus.CRASHED, retries_used=0)


def test_retry_on_failed():
    policy = RetryPolicy()
    assert policy.should_retry(TerminalStatus.FAILED, retries_used=0)


def test_no_retry_on_completed():
    policy = RetryPolicy()
    assert not policy.should_retry(TerminalStatus.COMPLETED, retries_used=0)


def test_retry_budget_exhausted():
    policy = RetryPolicy(max_retries=2)
    assert policy.should_retry(TerminalStatus.CRASHED, retries_used=1)
    assert not policy.should_retry(TerminalStatus.CRASHED, retries_used=2)
