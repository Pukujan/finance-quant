from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_two_artifacts_sorted(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0}, {"z": "2", "a": "1"})
    assert done.artifacts == (("a", "1"), ("z", "2"))
    ledger.close()
