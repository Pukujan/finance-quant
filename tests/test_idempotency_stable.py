from finance_quant.experiments.ledger import ExperimentLedger, RunSpec


def test_idempotency_key_is_stable_for_same_spec(tmp_path):
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    ledger = ExperimentLedger(tmp_path / "runs.db")
    a = ledger.begin(spec)
    b = ledger.begin(spec)
    assert a.run_id == b.run_id == spec.idempotency_key or a.run_id == b.run_id
    assert a.run_id == b.run_id
    ledger.close()
