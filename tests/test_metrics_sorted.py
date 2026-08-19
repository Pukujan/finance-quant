from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_metrics_are_sorted_on_the_record(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"z": 1.0, "a": 2.0, "m": 3.0})
    names = [n for n, _ in done.metrics]
    assert names == sorted(names)
    ledger.close()
