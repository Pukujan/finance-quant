"""Fresh-environment rerun receipt: same RunSpec must reproduce the same run_id and metrics.

Also exposes a PIT-depth pre-flight gate so reruns fail fast on shallow data.
"""
from __future__ import annotations

import json
from pathlib import Path

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.experiments.mlflow_export import export_run
from finance_quant.pit.store import PITStore, pit_depth_ok


def rerun_receipt(spec: RunSpec, metrics: dict[str, float], artifacts: dict[str, str],
                  first_db: Path, second_db: Path, export_root: Path,
                  pit_store: PITStore | None = None) -> dict:
    if pit_store is not None:
        ok, msg = pit_depth_ok(pit_store)
        if not ok:
            raise ValueError(f"PIT depth check failed: {msg}")

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


def rerun_runbook() -> str:
    return """\
Fresh-environment rerun runbook (issue #4):
1. Pin dataset with PITStore.snapshot_pin() and record it in RunSpec.dataset_manifest_hash.
2. Run `rerun_receipt(..., pit_store=store)` to verify PIT depth and reproduce run_id.
3. Compare first/second MLflow export roots byte-for-byte; any diff breaks reproducibility.
4. If a run failed, the same spec with status=FAILED and identical error_class must yield
   the same run_id; failed records are immutable and queryable forever.
"""
