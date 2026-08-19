from finance_quant.orchestration.authority import CapabilityClass, assert_worker_capability, worker_environment
import pytest
from finance_quant.orchestration.authority import AuthorityViolation


def test_sealed_scoring_worker_cannot_see_network_or_ledger():
    dirty = {
        "PATH": "x",
        "FQ_ATTEMPT_LEDGER_PATH": "/secret.db",
        "OPENAI_API_BASE": "https://api",
        "HTTPS_PROXY": "proxy",
    }
    env = worker_environment(CapabilityClass.SEALED_SCORING_WORKER, base=dirty)
    assert "FQ_ATTEMPT_LEDGER_PATH" not in env
    assert "OPENAI_API_BASE" not in env
    assert_worker_capability(env)
    with pytest.raises(AuthorityViolation):
        assert_worker_capability({**env, "FQ_SEALED_STORE": "bucket"})
