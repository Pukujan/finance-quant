"""Fail-closed public verifier for A1 sealed hidden-acceptance receipts.

This module never reads sealed cases or labels. It accepts only the public
``SealRecord`` commitment and the aggregate-only ``SafeAcceptanceReceipt`` that a
separate clean runner is permitted to emit.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .seal import SafeAcceptanceReceipt, SealRecord
from .uses import SealExhausted, assert_use_allowed


class A1HiddenAcceptanceError(ValueError):
    """Raised when an opaque A1 acceptance receipt cannot be trusted."""


_SEAL_KEYS = {
    "case_set_id",
    "case_merkle_root",
    "labels_hash",
    "sealed_at",
    "eval_harness_sha",
    "scorecard_ref",
    "max_uses",
}
_RECEIPT_KEYS = {
    "case_set_id",
    "commitment_hash",
    "candidate_artifact_hash",
    "status",
    "aggregate_metrics",
    "failure_classes",
    "use_number",
}


def _require_exact_keys(value: dict[str, Any], expected: set[str], *, kind: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise A1HiddenAcceptanceError(
            f"{kind} schema mismatch: missing={missing}, extra={extra}"
        )


def _require_sha256(value: str, *, field: str) -> None:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise A1HiddenAcceptanceError(f"{field} must be a lowercase sha256 hex digest")


def load_seal_record(path: str | Path) -> SealRecord:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise A1HiddenAcceptanceError("seal record must be a JSON object")
    _require_exact_keys(raw, _SEAL_KEYS, kind="seal record")
    record = SealRecord(**raw)
    _require_sha256(record.case_merkle_root, field="case_merkle_root")
    _require_sha256(record.labels_hash, field="labels_hash")
    if record.max_uses < 1:
        raise A1HiddenAcceptanceError("seal record max_uses must be positive")
    return record


def load_safe_receipt(path: str | Path) -> SafeAcceptanceReceipt:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise A1HiddenAcceptanceError("safe receipt must be a JSON object")
    _require_exact_keys(raw, _RECEIPT_KEYS, kind="safe receipt")

    metrics_raw = raw["aggregate_metrics"]
    if not isinstance(metrics_raw, list):
        raise A1HiddenAcceptanceError("aggregate_metrics must be a JSON array")
    metrics: list[tuple[str, float]] = []
    seen_metrics: set[str] = set()
    for item in metrics_raw:
        if not isinstance(item, list) or len(item) != 2:
            raise A1HiddenAcceptanceError("aggregate_metrics entries must be [name, value]")
        name, value = item
        if not isinstance(name, str) or not name:
            raise A1HiddenAcceptanceError("aggregate metric names must be non-empty strings")
        if name in seen_metrics:
            raise A1HiddenAcceptanceError(f"duplicate aggregate metric: {name}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise A1HiddenAcceptanceError(f"aggregate metric {name} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise A1HiddenAcceptanceError(f"aggregate metric {name} must be finite")
        seen_metrics.add(name)
        metrics.append((name, numeric))

    failures_raw = raw["failure_classes"]
    if not isinstance(failures_raw, list) or not all(
        isinstance(item, str) and item for item in failures_raw
    ):
        raise A1HiddenAcceptanceError("failure_classes must contain non-empty strings only")

    receipt = SafeAcceptanceReceipt(
        case_set_id=raw["case_set_id"],
        commitment_hash=raw["commitment_hash"],
        candidate_artifact_hash=raw["candidate_artifact_hash"],
        status=raw["status"],
        aggregate_metrics=tuple(metrics),
        failure_classes=tuple(failures_raw),
        use_number=raw["use_number"],
    )
    _require_sha256(receipt.commitment_hash, field="commitment_hash")
    _require_sha256(receipt.candidate_artifact_hash, field="candidate_artifact_hash")
    return receipt


def verify_a1_hidden_acceptance(
    record: SealRecord,
    receipt: SafeAcceptanceReceipt,
    *,
    expected_candidate_artifact_hash: str,
) -> SafeAcceptanceReceipt:
    """Verify one aggregate-only receipt without opening the sealed corpus.

    A passing receipt is accepted only when its public commitment, candidate
    identity, use budget, and aggregate-only schema all agree. Any ambiguity
    fails closed.
    """
    _require_sha256(expected_candidate_artifact_hash, field="expected_candidate_artifact_hash")
    if receipt.case_set_id != record.case_set_id:
        raise A1HiddenAcceptanceError("case_set_id does not match public seal record")
    if receipt.commitment_hash != record.commitment_hash:
        raise A1HiddenAcceptanceError("receipt commitment does not match public seal record")
    if receipt.candidate_artifact_hash != expected_candidate_artifact_hash:
        raise A1HiddenAcceptanceError("receipt candidate artifact hash mismatch")
    try:
        assert_use_allowed(record, receipt.use_number)
    except SealExhausted as exc:
        raise A1HiddenAcceptanceError(str(exc)) from exc
    if receipt.status != "pass":
        raise A1HiddenAcceptanceError(f"hidden acceptance did not pass: {receipt.status}")
    if receipt.failure_classes:
        raise A1HiddenAcceptanceError("passing hidden receipt cannot contain failure classes")
    return receipt
