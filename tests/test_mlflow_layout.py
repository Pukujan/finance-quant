from pathlib import Path

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.experiments.mlflow_export import export_run


def test_mlflow_export_creates_expected_directories(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0}, {"a": "ref"})
    run_dir = export_run(done, tmp_path / "mlflow")
    assert (run_dir / "meta.json").exists()
    assert (run_dir / "params" / "experiment_id").exists()
    assert (run_dir / "metrics" / "x").exists()
    assert (run_dir / "artifacts" / "a.ref").exists()
    ledger.close()
