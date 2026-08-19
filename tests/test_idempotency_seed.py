from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_idempotency_key_differs_when_seed_differs():
    a = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    b = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (2,), "split", "cost")
    assert a.idempotency_key != b.idempotency_key
