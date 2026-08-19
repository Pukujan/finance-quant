from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_partial_metrics_do_not_look_like_completed_campaign(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("partial", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.status is RunStatus.RUNNING
    assert run.completed_at is None
    ledger.close()
