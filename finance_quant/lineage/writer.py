"""End-to-end ontology v0.1 evidence writer for the vertical slice (issue #6).

This module is the narrow integration point between a run result and the
FOSSIL-shaped evidence pack. It enforces the ontology boundary rules and emits
exactly one evidence commit per run, returning a stable reference hash.
"""
from __future__ import annotations

from finance_quant.experiments.ledger import RunRecord
from finance_quant.lineage.evidence import EvidenceCommit, OntologyError, evidence_payload
from finance_quant.lineage.pack import LocalEvidencePack


def commit_run_evidence(
    pack: LocalEvidencePack,
    record: RunRecord,
    snapshot_hash: str,
    activity_type: str = "ExperimentRun",
    known_at: str = "2026-08-19",
) -> str:
    """Write a single, validated ontology v0.1 evidence commit for a run record.

    Raises:
        OntologyError: if the record or arguments violate the v0.1 ontology.
    """
    if not record or not record.run_id:
        raise OntologyError("run record and run_id are required")
    if not snapshot_hash:
        raise OntologyError("snapshot_hash is required")

    commit = EvidenceCommit(
        entity_type="RunRecord",
        entity_hash=record.run_id,
        activity_type=activity_type,
        known_at=known_at,
        derived_from=(snapshot_hash, record.spec.feature_ir_hash),
        decided_by=None,
    )
    path = pack.commit(commit)
    return commit.hash


def evidence_reference(run_id: str, snapshot_hash: str) -> dict:
    """Return a lightweight, hashable reference suitable for run records / receipts."""
    return {
        "type": "finance_quant_evidence_reference",
        "run_id": run_id,
        "snapshot_hash": snapshot_hash,
    }
