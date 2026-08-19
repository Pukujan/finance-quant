from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_run_id_is_64_hex(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert len(run.run_id) == 64
    assert all(c in "0123456789abcdef" for c in run.run_id)
    ledger.close()
