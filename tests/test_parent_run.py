from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_parent_run_id_is_recorded(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    parent = ledger.begin(RunSpec("p", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost"))
    parent = ledger.finalize(parent.run_id, RunStatus.SUCCESS, {"x": 1.0})
    child = ledger.begin(RunSpec("c", "c" * 40, "env", "data", "ir", "model", (2,), "split", "cost",
                                 parent_run_id=parent.run_id))
    assert child.spec.parent_run_id == parent.run_id
    ledger.close()
