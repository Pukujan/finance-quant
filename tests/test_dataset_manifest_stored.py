from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_dataset_manifest_hash_is_stored(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "manifest-xyz", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.dataset_manifest_hash == "manifest-xyz"
    ledger.close()
