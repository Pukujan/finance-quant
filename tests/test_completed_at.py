from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_completed_at_is_set_on_success(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.completed_at is None
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.completed_at is not None
    assert done.completed_at >= run.created_at
    ledger.close()
