from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_created_at_is_positive(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    assert run.created_at > 0
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
