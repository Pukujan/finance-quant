"""Attach FOSSIL-shaped evidence commits to B1-B5 run records (cold path only)."""
from __future__ import annotations

from finance_quant.experiments.ledger import RunRecord
from finance_quant.lineage.evidence import EvidenceCommit, evidence_payload


def evidence_commit_for_run(record: RunRecord, snapshot_hash: str) -> EvidenceCommit:
    return EvidenceCommit(
        entity_type="RunRecord",
        entity_hash=record.run_id,
        activity_type="ExperimentRun",
        known_at="2026-08-19",
        derived_from=(snapshot_hash, record.spec.feature_ir_hash),
        decided_by=None,
    )


def evidence_for_run(record: RunRecord, snapshot_hash: str) -> dict:
    return evidence_payload(evidence_commit_for_run(record, snapshot_hash))
