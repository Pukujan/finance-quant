from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_split_policy_and_cost_model_are_required_and_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "walk-forward-v0", "c-stress2x")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.split_policy_ref == "walk-forward-v0"
    assert done.spec.cost_model_ref == "c-stress2x"
    ledger.close()
