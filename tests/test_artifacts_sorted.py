from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_artifacts_are_sorted_on_the_record(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0}, {"z": "2", "a": "1"})
    names = [n for n, _ in done.artifacts]
    assert names == sorted(names)
    ledger.close()
