from finance_quant.orchestration.executor import environment_hash


def test_environment_hash_is_stable_within_process():
    assert environment_hash() == environment_hash()
    assert len(environment_hash()) == 64
