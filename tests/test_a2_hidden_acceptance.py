from __future__ import annotations

import json

import pytest

from finance_quant.acceptance.a2_hidden import (
    A2HiddenAcceptanceError,
    A2_SCORECARD_REF,
    load_a2_safe_receipt,
    load_a2_seal_record,
    verify_a2_hidden_acceptance,
)
from finance_quant.acceptance.seal import SafeAcceptanceReceipt, SealRecord

PUBLIC_SHA = "c" * 40
CANDIDATE_HASH = "d" * 64


def _record(**overrides) -> SealRecord:
    values = {
        "case_set_id": "A2-ISSUE-16-HIDDEN-V1",
        "case_merkle_root": "a" * 64,
        "labels_hash": "b" * 64,
        "sealed_at": "2026-08-27T00:00:00Z",
        "eval_harness_sha": PUBLIC_SHA,
        "scorecard_ref": A2_SCORECARD_REF,
        "max_uses": 1,
    }
    values.update(overrides)
    return SealRecord(**values)


def _receipt(record: SealRecord, **overrides) -> SafeAcceptanceReceipt:
    values = {
        "case_set_id": record.case_set_id,
        "commitment_hash": record.commitment_hash,
        "candidate_artifact_hash": CANDIDATE_HASH,
        "status": "pass",
        "aggregate_metrics": (("conformant", 1.0), ("evaluated", 1.0)),
        "failure_classes": (),
        "use_number": 1,
    }
    values.update(overrides)
    return SafeAcceptanceReceipt(**values)


def test_a2_verifier_accepts_only_frozen_one_shot_full_conformance():
    record = _record()
    receipt = _receipt(record)
    assert verify_a2_hidden_acceptance(
        record,
        receipt,
        expected_candidate_artifact_hash=CANDIDATE_HASH,
        expected_public_eval_sha=PUBLIC_SHA,
    ) == receipt


@pytest.mark.parametrize(
    ("record_overrides", "receipt_overrides", "expected_sha", "message"),
    [
        ({"case_set_id": "A1-WRONG"}, {}, PUBLIC_SHA, "begin with A2"),
        ({"eval_harness_sha": "e" * 40}, {}, PUBLIC_SHA, "eval_harness_sha"),
        ({"scorecard_ref": "wrong"}, {}, PUBLIC_SHA, "scorecard_ref"),
        ({"max_uses": 2}, {}, PUBLIC_SHA, "one-shot"),
        ({}, {"candidate_artifact_hash": "e" * 64}, PUBLIC_SHA, "candidate artifact"),
        ({}, {"status": "fail"}, PUBLIC_SHA, "did not pass"),
        ({}, {"failure_classes": ("ACCOUNT_REPLAY",)}, PUBLIC_SHA, "failure classes"),
        ({}, {"use_number": 2}, PUBLIC_SHA, "use_number"),
        ({}, {"aggregate_metrics": (("conformant", 0.0), ("evaluated", 1.0))}, PUBLIC_SHA, "full conformance"),
        ({}, {"aggregate_metrics": (("conformant", 1.0),)}, PUBLIC_SHA, "exactly conformant and evaluated"),
        ({}, {}, "not-a-sha", "40-hex"),
    ],
)
def test_a2_verifier_fails_closed_on_any_public_identity_or_aggregate_drift(
    record_overrides, receipt_overrides, expected_sha, message
):
    record = _record(**record_overrides)
    receipt = _receipt(record, **receipt_overrides)
    with pytest.raises(A2HiddenAcceptanceError, match=message):
        verify_a2_hidden_acceptance(
            record,
            receipt,
            expected_candidate_artifact_hash=CANDIDATE_HASH,
            expected_public_eval_sha=expected_sha,
        )


def test_a2_loaders_reject_extra_fields_that_could_leak_hidden_material(tmp_path):
    record = _record()
    seal = {
        "case_set_id": record.case_set_id,
        "case_merkle_root": record.case_merkle_root,
        "labels_hash": record.labels_hash,
        "sealed_at": record.sealed_at,
        "eval_harness_sha": record.eval_harness_sha,
        "scorecard_ref": record.scorecard_ref,
        "max_uses": record.max_uses,
        "case_ids": ["forbidden"],
    }
    seal_path = tmp_path / "seal.json"
    seal_path.write_text(json.dumps(seal), encoding="utf-8")
    with pytest.raises(A2HiddenAcceptanceError, match="extra=.*case_ids"):
        load_a2_seal_record(seal_path)

    receipt = _receipt(record)
    safe = {
        "case_set_id": receipt.case_set_id,
        "commitment_hash": receipt.commitment_hash,
        "candidate_artifact_hash": receipt.candidate_artifact_hash,
        "status": receipt.status,
        "aggregate_metrics": [["conformant", 1.0], ["evaluated", 1.0]],
        "failure_classes": [],
        "use_number": 1,
        "traces": ["forbidden"],
    }
    safe_path = tmp_path / "receipt.json"
    safe_path.write_text(json.dumps(safe), encoding="utf-8")
    with pytest.raises(A2HiddenAcceptanceError, match="extra=.*traces"):
        load_a2_safe_receipt(safe_path)
