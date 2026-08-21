"""Phase B Qlib train/eval path with MLflow-compatible lineage.

This is a credential-free stub that records the lineage fields required for a
reproducible benchmark without requiring a real Qlib or LightGBM install.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "manifest_id": "canonical-fixture-v0",
            "snapshot_pin": "a" * 64,
            "pinned_kt": "2024-01-02T16:00:01.123000-05:00",
            "symbols": ["AAA", "BBB"],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def build_qlib_extract(manifest: dict[str, Any]) -> dict[str, Any]:
    """Stub Qlib-format extract pinned at manifest['pinned_kt']."""
    return {
        "dataset_manifest_hash": manifest.get("snapshot_pin"),
        "pinned_kt": manifest.get("pinned_kt"),
        "symbols": manifest.get("symbols", []),
        "features": ["$open", "$high", "$low", "$close", "$volume"],
        "n_rows": len(manifest.get("symbols", [])) * 10,
    }


def compute_feature_ir_hash(extract: dict[str, Any]) -> str:
    return content_hash({"features": extract["features"], "pinned_kt": extract["pinned_kt"]})


def train_lightgbm_stub(extract: dict[str, Any]) -> tuple[dict[str, Any], str]:
    model_config = {
        "objective": "regression",
        "metric": "rmse",
        "num_leaves": 31,
        "learning_rate": 0.05,
    }
    predictions = {
        "AAA": [0.01] * 10,
        "BBB": [-0.005] * 10,
    }
    return predictions, content_hash(model_config)


def log_mlflow_run(
    out_dir: Path,
    manifest: dict[str, Any],
    extract: dict[str, Any],
    predictions: dict[str, Any],
    model_config_hash: str,
    status: str,
    error: str | None = None,
) -> Path:
    run = {
        "run_id": "qlib-phase-b-" + content_hash(manifest)[:12],
        "status": status,
        "dataset_manifest_hash": manifest.get("snapshot_pin"),
        "feature_ir_hash": compute_feature_ir_hash(extract),
        "model_config_hash": model_config_hash,
        "split_policy_ref": "chronological-80-20-v0",
        "cost_model_ref": "nominal-5bps-slippage-v0",
        "predictions_hash": content_hash(predictions),
        "error": error,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "mlflow_run.json"
    path.write_text(canonical_json(run) + "\n", encoding="utf-8")
    return run


def record_ledger(out_dir: Path, run: dict[str, Any]) -> Path:
    path = out_dir / "experiment_ledger_receipts.jsonl"
    receipt = {
        "receipt_type": "ExperimentLedger",
        "run_id": run["run_id"],
        "status": run["status"],
        "dataset_manifest_hash": run["dataset_manifest_hash"],
        "feature_ir_hash": run["feature_ir_hash"],
        "model_config_hash": run["model_config_hash"],
        "split_policy_ref": run["split_policy_ref"],
        "cost_model_ref": run["cost_model_ref"],
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(canonical_json(receipt) + "\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase B Qlib train/eval stub")
    parser.add_argument("--fixture-manifest", type=Path, default=Path("data/fixtures/phase-b/manifest.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/qlib_phase_b"))
    parser.add_argument("--fail-drill", action="store_true", help="force a mid-training failure")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.fixture_manifest)
    extract = build_qlib_extract(manifest)

    if args.fail_drill:
        run = log_mlflow_run(
            args.out_dir, manifest, extract, {}, "", "FAILED",
            error="forced mid-training failure for drill",
        )
        record_ledger(args.out_dir, run)
        print(f"fail-drill recorded: {run}")
        return 0

    predictions, model_config_hash = train_lightgbm_stub(extract)
    run = log_mlflow_run(args.out_dir, manifest, extract, predictions, model_config_hash, "SUCCESS")
    record_ledger(args.out_dir, run)
    print(f"logged: {run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
