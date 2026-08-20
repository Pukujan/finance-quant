"""Trial Gate V0: executable artifact validation for Phase B campaign trials.

The gate is intentionally local, deterministic, and credential-free. It checks
that a trial artifact satisfies the minimum invariant contract before it can be
admitted as evidence. It does NOT replace sealed-holdout acceptance; it is a
pre-filter that keeps obviously invalid artifacts out of promotion evidence.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "run_id", "experiment_id", "dataset_manifest_hash", "feature_ir_hash",
    "model_config_hash", "code_sha", "env_lock_hash", "seeds", "split_policy_ref",
    "cost_model_ref", "agent_origin", "status", "artifacts", "metrics",
}


class TrialGateError(ValueError):
    """Raised when a trial artifact fails the V0 admission gate."""


@dataclass(frozen=True)
class GateResult:
    ok: bool
    violations: list[str]


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and re.fullmatch(r"[0-9a-fA-F]+", value) is not None


def _validate_hash_field(artifact: dict, name: str, violations: list[str]) -> None:
    value = artifact.get(name)
    if not value:
        violations.append(f"missing {name}")
    elif not _is_hex64(value):
        violations.append(f"{name} must be a 64-char hex string")


def check_trial_artifact(artifact: dict) -> GateResult:
    """Run the V0 admission checks on a trial artifact dictionary."""
    violations: list[str] = []

    # 1. Required fields present.
    missing = REQUIRED_FIELDS - set(artifact.keys())
    if missing:
        violations.append(f"missing required fields: {sorted(missing)}")

    # 2. Provenance hashes.
    for field in ("dataset_manifest_hash", "feature_ir_hash", "model_config_hash",
                  "code_sha", "env_lock_hash"):
        _validate_hash_field(artifact, field, violations)

    # 3. Seeds must be non-empty and deterministic.
    seeds = artifact.get("seeds")
    if not seeds:
        violations.append("seeds must be non-empty")
    elif not isinstance(seeds, (list, tuple)) or not all(isinstance(s, int) for s in seeds):
        violations.append("seeds must be a list of ints")

    # 4. Status must be terminal.
    status = artifact.get("status")
    if status not in {"success", "failed", "invalid"}:
        violations.append(f"status {status!r} is not a terminal value")

    # 5. Artifacts must declare every expected key and a hash.
    artifacts = artifact.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        violations.append("artifacts must be a dict")
    else:
        for key, value in artifacts.items():
            if not _is_hex64(value):
                violations.append(f"artifact {key!r} value must be a 64-char hex hash")

    # 6. PIT leakage sentinel: feature_ir_hash must not reference a label field.
    feature_ir = str(artifact.get("feature_ir_hash", ""))
    if "label" in feature_ir.lower() or "target" in feature_ir.lower():
        violations.append("feature_ir_hash contains label/target sentinel (leakage)")

    # 7. Poison sentinel: metrics must not claim a sealed/unsealed delta that is
    #    implausibly perfect without an explicit skipped-contamination note.
    metrics = artifact.get("metrics") or {}
    sealed = metrics.get("sealed_score")
    unsealed = metrics.get("unsealed_score")
    skipped = artifact.get("skipped_contamination_check") is True
    if sealed is not None and unsealed is not None and not skipped:
        from finance_quant.acceptance.contamination import contamination_flag
        if contamination_flag(unsealed, sealed):
            violations.append("contamination sentinel triggered: sealed score implausibly better")

    return GateResult(ok=not violations, violations=violations)


def check_trial_artifact_file(path: str | Path) -> GateResult:
    """Load a JSON artifact and run the V0 gate."""
    p = Path(path)
    if not p.is_file():
        return GateResult(False, [f"artifact file not found: {p}"])
    try:
        artifact = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GateResult(False, [f"invalid JSON: {exc}"])
    if not isinstance(artifact, dict):
        return GateResult(False, ["artifact must be a JSON object"])
    return check_trial_artifact(artifact)
