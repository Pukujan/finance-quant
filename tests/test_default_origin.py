from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_agent_origin_defaults_to_human(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.agent_origin == "human"
    ledger.close()
