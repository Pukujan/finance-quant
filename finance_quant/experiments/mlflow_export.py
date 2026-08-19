"""MLflow-compatible export, without requiring MLflow as a V0 runtime dependency.

The exported layout follows MLflow's file-store primitives (experiment/run meta,
params, metrics, artifacts). An adapter may upload it to a tracking server later;
the ExperimentLedger remains authoritative.
"""
from __future__ import annotations

import json
from pathlib import Path

from .ledger import RunRecord


def export_run(record: RunRecord, root: str | Path) -> Path:
    root = Path(root)
    run_dir = root / record.spec.experiment_id / record.run_id
    (run_dir / "params").mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics").mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
    (run_dir / "meta.json").write_text(json.dumps({
        "run_id": record.run_id, "status": record.status.value,
        "created_at": record.created_at, "completed_at": record.completed_at,
        "error_class": record.error_class, "parent_run_id": record.spec.parent_run_id,
        "agent_origin": record.spec.agent_origin,
    }, sort_keys=True, indent=2))
    for name, value in record.spec.__dict__.items():
        (run_dir / "params" / name).write_text(json.dumps(value, sort_keys=True, default=list))
    for name, value in record.metrics:
        (run_dir / "metrics" / name).write_text(str(value))
    for name, artifact_hash in record.artifacts:
        (run_dir / "artifacts" / f"{name}.ref").write_text(artifact_hash)
    return run_dir
