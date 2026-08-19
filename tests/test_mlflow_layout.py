from finance_quant.experiments.mlflow_export import export_run
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from pathlib import Path


def test_mlflow_export_layout_has_params_metrics_artifacts(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.5}, {"a": "hash"})
    out = export_run(done, tmp_path / "mlruns")
    assert (out / "params" / "code_sha").exists()
    assert (out / "metrics" / "x").read_text() == "1.5"
    assert (out / "artifacts" / "a.ref").read_text() == "hash"
    ledger.close()
