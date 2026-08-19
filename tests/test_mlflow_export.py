from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.experiments.mlflow_export import export_run


def test_mlflow_compatible_export_preserves_authoritative_run_fields(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    started = ledger.begin(spec)
    done = ledger.finalize(started.run_id, RunStatus.SUCCESS, {"ic": .1}, {"model": "abc"})
    out = export_run(done, tmp_path / "mlruns")
    assert (out / "params" / "dataset_manifest_hash").read_text() == '"data"'
    assert (out / "metrics" / "ic").read_text() == "0.1"
    assert (out / "artifacts" / "model.ref").read_text() == "abc"
    ledger.close()
