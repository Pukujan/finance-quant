from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_begin_does_not_write_metrics(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.metrics == ()
    assert run.status.value == "running"
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
