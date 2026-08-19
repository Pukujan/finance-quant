from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_success_metrics_single_pair(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"rank_ic": -0.5})
    assert done.metrics == (("rank_ic", -0.5),)
    ledger.close()
