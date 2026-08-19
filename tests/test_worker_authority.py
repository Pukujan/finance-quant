import pytest

from finance_quant.orchestration.authority import (
    FORBIDDEN_WORKER_VARS,
    AuthorityViolation,
    CapabilityClass,
    assert_worker_capability,
    worker_environment,
)


def test_worker_environment_strips_forbidden_handles():
    base = {v: "secret" for v in FORBIDDEN_WORKER_VARS}
    base["PATH"] = "/bin"
    env = worker_environment(CapabilityClass.RESEARCH_WORKER, base)
    for v in FORBIDDEN_WORKER_VARS:
        assert v not in env
    assert env["FQ_CAPABILITY"] == "research_worker"


def test_assert_worker_capability_raises_on_forbidden_handles():
    env = {"FQ_CAPABILITY": "research_worker", "FQ_ATTEMPT_LEDGER_PATH": "x"}
    with pytest.raises(AuthorityViolation, match="FQ_ATTEMPT_LEDGER_PATH"):
        assert_worker_capability(env)
