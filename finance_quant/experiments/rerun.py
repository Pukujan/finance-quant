"""Fresh-environment rerun receipt: same RunSpec must reproduce the same run_id and metrics."""
from __future__ import annotations

import json
from pathlib import Path

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.experiments.mlflow_export import export_run


def rerun_receipt(spec: RunSpec, metrics: dict[str, float], artifacts: dict[str, str],
                  first_db: Path, second_db: Path, export_root: Path) -> dict:
    first = ExperimentLedger(first_db)
    a = first.begin(spec)
    a = first.finalize(a.run_id, RunStatus.SUCCESS, metrics, artifacts)
    export_run(a, export_root / "first")
    first.close()

    second = ExperimentLedger(second_db)
    b = second.begin(spec)
    b = second.finalize(b.run_id, RunStatus.SUCCESS, metrics, artifacts)
    export_run(b, export_root / "second")
    second.close()
    return {
        "same_run_id": a.run_id == b.run_id,
        "same_metrics": a.metrics == b.metrics,
        "same_spec_hash": a.spec.idempotency_key == b.spec.idempotency_key,
        "run_id": a.run_id,
    }
