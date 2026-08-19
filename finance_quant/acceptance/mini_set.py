"""Sealed mini-case commitment without exposing cases or labels (spike #9)."""
from __future__ import annotations

import json
from pathlib import Path

from .seal import SafeAcceptanceReceipt, SealRecord, _hash, merkle_root


def make_mini_set_commitment(case_hashes: list[str], labels_hash: str, eval_harness_sha: str,
                             max_uses: int = 2, case_set_id: str = "SEAL-MINI-A") -> SealRecord:
    """Build a public SealRecord from a list of case sha256s; never accepts raw cases/labels."""
    return SealRecord(
        case_set_id=case_set_id,
        case_merkle_root=merkle_root(case_hashes),
        labels_hash=labels_hash,
        sealed_at="2026-08-19T00:00:00Z",
        eval_harness_sha=eval_harness_sha,
        scorecard_ref="docs/acceptance/SEALED_INTERFACE.md",
        max_uses=max_uses,
    )


def write_mini_set_receipt(record: SealRecord, candidate_artifact_hash: str,
                           aggregate_metrics: dict[str, float], failure_classes: list[str],
                           out: str | Path) -> Path:
    receipt = SafeAcceptanceReceipt(
        case_set_id=record.case_set_id,
        commitment_hash=record.commitment_hash,
        candidate_artifact_hash=candidate_artifact_hash,
        status="pass" if not failure_classes else "fail",
        aggregate_metrics=tuple(sorted(aggregate_metrics.items())),
        failure_classes=tuple(sorted(failure_classes)),
        use_number=1,
    )
    out = Path(out)
    out.write_text(json.dumps({
        "case_set_id": receipt.case_set_id,
        "commitment_hash": receipt.commitment_hash,
        "candidate_artifact_hash": receipt.candidate_artifact_hash,
        "status": receipt.status,
        "aggregate_metrics": dict(receipt.aggregate_metrics),
        "failure_classes": list(receipt.failure_classes),
        "use_number": receipt.use_number,
        "max_uses": record.max_uses,
        "case_merkle_root": record.case_merkle_root,
        "labels_hash": record.labels_hash,
    }, sort_keys=True, indent=2))
    return out
