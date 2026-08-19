from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_invalid_run_metrics_default_empty(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.INVALID, error_class="X")
    assert done.metrics == ()
    ledger.close()
