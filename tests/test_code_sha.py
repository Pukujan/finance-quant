from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_code_sha_is_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    sha = "deadbeef" * 5
    spec = RunSpec("e", sha, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.code_sha == sha
    ledger.close()
