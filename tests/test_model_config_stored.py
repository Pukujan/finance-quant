from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_model_config_hash_is_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "lgbm-v0", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.model_config_hash == "lgbm-v0"
    ledger.close()
