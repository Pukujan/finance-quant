from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_experiment_id_is_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("B2-sma3-walk-forward", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.experiment_id == "B2-sma3-walk-forward"
    ledger.close()
