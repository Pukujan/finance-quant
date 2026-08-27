"""Fail-closed public verifier for A2 sealed hidden-acceptance receipts.

This module consumes only the public SealRecord commitment and aggregate-only
SafeAcceptanceReceipt. It never opens sealed cases, labels, case IDs, traces, or
oracle internals.
"""
from __future__ import annotations

import math
from pathlib import Path

from .a1_hidden import (
    A1HiddenAcceptanceError,
    load_safe_receipt as _load_safe_receipt,
    load_seal_record as _load_seal_record,
    verify_a1_hidden_acceptance,
)
from .seal import SafeAcceptanceReceipt, SealRecord

A2_SCORECARD_REF = "issue-16-a2-public-contract-v1"


class A2HiddenAcceptanceError(ValueError):
    """Raised when aggregate A2 hidden evidence cannot be trusted."""


def _require_git_sha(value: str, *, field: str) -> None:
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise A2HiddenAcceptanceError(f"{field} must be a lowercase 40-hex git commit SHA")


def load_a2_seal_record(path: str | Path) -> SealRecord:
    try:
        return _load_seal_record(path)
    except (A1HiddenAcceptanceError, ValueError, TypeError) as exc:
        raise A2HiddenAcceptanceError(str(exc)) from exc


def load_a2_safe_receipt(path: str | Path) -> SafeAcceptanceReceipt:
    try:
        return _load_safe_receipt(path)
    except (A1HiddenAcceptanceError, ValueError, TypeError) as exc:
        raise A2HiddenAcceptanceError(str(exc)) from exc


def _validate_aggregate_metrics(receipt: SafeAcceptanceReceipt) -> None:
    metrics: dict[str, float] = {}
    for name, value in receipt.aggregate_metrics:
        if not isinstance(name, str) or not name:
            raise A2HiddenAcceptanceError("aggregate metric names must be non-empty strings")
        if name in metrics:
            raise A2HiddenAcceptanceError(f"duplicate aggregate metric: {name}")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise A2HiddenAcceptanceError(f"aggregate metric {name} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise A2HiddenAcceptanceError(f"aggregate metric {name} must be finite")
        metrics[name] = numeric
    if set(metrics) != {"conformant", "evaluated"}:
        raise A2HiddenAcceptanceError(
            "A2 safe receipt metrics must be exactly conformant and evaluated"
        )
    if metrics["conformant"] != 1.0 or metrics["evaluated"] != 1.0:
        raise A2HiddenAcceptanceError("A2 hidden aggregate did not report full conformance")


def verify_a2_hidden_acceptance(
    record: SealRecord,
    receipt: SafeAcceptanceReceipt,
    *,
    expected_candidate_artifact_hash: str,
    expected_public_eval_sha: str,
) -> SafeAcceptanceReceipt:
    """Verify one one-shot A2 aggregate receipt without opening the holdout."""
    _require_git_sha(expected_public_eval_sha, field="expected_public_eval_sha")
    if not record.case_set_id.startswith("A2-"):
        raise A2HiddenAcceptanceError("A2 seal case_set_id must begin with A2-")
    if record.eval_harness_sha != expected_public_eval_sha:
        raise A2HiddenAcceptanceError("seal eval_harness_sha does not match frozen public evaluation SHA")
    if record.scorecard_ref != A2_SCORECARD_REF:
        raise A2HiddenAcceptanceError("seal scorecard_ref does not match the A2 public contract")
    if record.max_uses != 1:
        raise A2HiddenAcceptanceError("A2 hidden seal must be one-shot with max_uses=1")
    if receipt.use_number != 1:
        raise A2HiddenAcceptanceError("A2 hidden receipt must use the sole authorized use_number=1")
    try:
        verified = verify_a1_hidden_acceptance(
            record,
            receipt,
            expected_candidate_artifact_hash=expected_candidate_artifact_hash,
        )
    except (A1HiddenAcceptanceError, ValueError, TypeError) as exc:
        raise A2HiddenAcceptanceError(str(exc)) from exc
    _validate_aggregate_metrics(verified)
    return verified
