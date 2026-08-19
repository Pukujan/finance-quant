from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_begin_status_is_running(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.status is RunStatus.RUNNING
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
