from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_begin_artifacts_empty(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.artifacts == ()
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
