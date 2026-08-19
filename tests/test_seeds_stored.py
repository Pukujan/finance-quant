from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_seeds_are_stored_as_tuple(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (7, 8, 9), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.seeds == (7, 8, 9)
    ledger.close()
