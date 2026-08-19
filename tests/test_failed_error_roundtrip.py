from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_failed_error_class_round_trip(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.FAILED, error_class="OSError")
    assert ledger.get(done.run_id).error_class == "OSError"
    ledger.close()
