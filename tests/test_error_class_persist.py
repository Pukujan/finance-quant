from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_error_class_persists_on_failed_run(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.FAILED, error_class="TimeoutError")
    assert ledger.get(run.run_id).error_class == "TimeoutError"
    assert done.status is RunStatus.FAILED
    ledger.close()
