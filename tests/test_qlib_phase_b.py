import json
from pathlib import Path

from scripts.run_qlib_phase_b import (
    build_qlib_extract,
    compute_feature_ir_hash,
    content_hash,
    load_manifest,
    log_mlflow_run,
    main,
    train_lightgbm_stub,
)


def test_load_manifest_default():
    manifest = load_manifest(Path("nonexistent.json"))
    assert "snapshot_pin" in manifest
    assert "pinned_kt" in manifest


def test_build_qlib_extract():
    manifest = {"snapshot_pin": "abc", "pinned_kt": "kt1", "symbols": ["X", "Y"]}
    extract = build_qlib_extract(manifest)
    assert extract["dataset_manifest_hash"] == "abc"
    assert extract["pinned_kt"] == "kt1"
    assert "$close" in extract["features"]


def test_compute_feature_ir_hash():
    extract = {"features": ["$open"], "pinned_kt": "kt1"}
    h1 = compute_feature_ir_hash(extract)
    h2 = compute_feature_ir_hash(extract)
    assert h1 == h2
    assert len(h1) == 64


def test_train_lightgbm_stub():
    extract = {"features": ["$open"], "pinned_kt": "kt1"}
    predictions, model_hash = train_lightgbm_stub(extract)
    assert set(predictions.keys()) == {"AAA", "BBB"}
    assert len(model_hash) == 64


def test_log_mlflow_run_fields(tmp_path):
    manifest = {"snapshot_pin": "a" * 64}
    extract = {"features": ["$open"], "pinned_kt": "kt1"}
    predictions = {"X": [0.1]}
    run = log_mlflow_run(tmp_path, manifest, extract, predictions, "b" * 64, "SUCCESS")
    assert run["dataset_manifest_hash"] == "a" * 64
    assert run["feature_ir_hash"] == compute_feature_ir_hash(extract)
    assert run["model_config_hash"] == "b" * 64
    assert run["split_policy_ref"]
    assert run["cost_model_ref"]
    assert (tmp_path / "mlflow_run.json").exists()


def test_main_success(tmp_path):
    out_dir = tmp_path / "qlib"
    code = main(["--out-dir", str(out_dir)])
    assert code == 0
    assert (out_dir / "mlflow_run.json").exists()
    assert (out_dir / "experiment_ledger_receipts.jsonl").exists()


def test_main_fail_drill(tmp_path):
    out_dir = tmp_path / "qlib"
    code = main(["--out-dir", str(out_dir), "--fail-drill"])
    assert code == 0
    run = json.loads((out_dir / "mlflow_run.json").read_text())
    assert run["status"] == "FAILED"
    assert "forced" in run["error"]
