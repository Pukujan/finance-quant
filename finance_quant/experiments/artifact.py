"""Helpers to produce Trial Gate V0-compatible artifact dictionaries from runs."""
from __future__ import annotations

from finance_quant.experiments.ledger import RunRecord


def run_record_to_trial_artifact(record: RunRecord) -> dict:
    """Serialize a RunRecord into the Trial Gate V0 artifact schema."""
    return {
        "run_id": record.run_id,
        "experiment_id": record.spec.experiment_id,
        "dataset_manifest_hash": record.spec.dataset_manifest_hash,
        "feature_ir_hash": record.spec.feature_ir_hash,
        "model_config_hash": record.spec.model_config_hash,
        "code_sha": record.spec.code_sha,
        "env_lock_hash": record.spec.env_lock_hash,
        "seeds": list(record.spec.seeds),
        "split_policy_ref": record.spec.split_policy_ref,
        "cost_model_ref": record.spec.cost_model_ref,
        "agent_origin": record.spec.agent_origin,
        "status": record.status.value,
        "artifacts": dict(record.artifacts),
        "metrics": dict(record.metrics),
    }
