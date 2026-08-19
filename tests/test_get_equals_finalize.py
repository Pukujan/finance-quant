from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_get_returns_same_record_as_finalize(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"ic": 0.2})
    assert ledger.get(run.run_id) == done
    ledger.close()
