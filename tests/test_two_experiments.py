from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_two_experiments_have_different_run_ids(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    a = ledger.begin(RunSpec("A", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost"))
    b = ledger.begin(RunSpec("B", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost"))
    assert a.run_id != b.run_id
    ledger.finalize(a.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.finalize(b.run_id, RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
