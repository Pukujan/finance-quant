from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_invalid_runs_are_terminal_and_visible(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("inv", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.INVALID, error_class="TemporalError")
    assert done.status is RunStatus.INVALID
    assert ledger.get(run.run_id).error_class == "TemporalError"
    ledger.close()
