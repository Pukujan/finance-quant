from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_env_lock_hash_is_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "lock-abc", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.env_lock_hash == "lock-abc"
    ledger.close()
