from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_three_metrics_sorted(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"c": 3.0, "a": 1.0, "b": 2.0})
    assert [n for n, _ in done.metrics] == ["a", "b", "c"]
    ledger.close()
