from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_two_metrics_sorted(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"b": 2.0, "a": 1.0})
    assert done.metrics == (("a", 1.0), ("b", 2.0))
    ledger.close()
