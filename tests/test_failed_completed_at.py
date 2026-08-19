from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_failed_completed_at_is_set(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.FAILED, error_class="X")
    assert done.completed_at is not None
    ledger.close()
