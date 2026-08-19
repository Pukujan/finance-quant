from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_finalize_success_clears_error_class(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.error_class is None
    ledger.close()
