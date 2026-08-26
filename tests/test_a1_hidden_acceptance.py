import json

import pytest

from finance_quant.acceptance.a1_hidden import (
    A1HiddenAcceptanceError,
    load_safe_receipt,
    load_seal_record,
    verify_a1_hidden_acceptance,
)
from finance_quant.acceptance.seal import SafeAcceptanceReceipt, SealRecord


def _record() -> SealRecord:
    return SealRecord(
        case_set_id="A1-EXECUTION-HIDDEN",
        case_merkle_root="a" * 64,
        labels_hash="b" * 64,
        sealed_at="2026-08-25T00:00:00Z",
        eval_harness_sha="c" * 40,
        scorecard_ref="a1-execution-v1",
        max_uses=2,
    )


def _receipt(record: SealRecord, *, status: str = "pass", use_number: int = 1):
    return SafeAcceptanceReceipt(
        case_set_id=record.case_set_id,
        commitment_hash=record.commitment_hash,
        candidate_artifact_hash="d" * 64,
        status=status,
        aggregate_metrics=(("score", 1.0),),
        failure_classes=(),
        use_number=use_number,
    )


def test_verifier_accepts_only_matching_passing_aggregate_receipt():
    record = _record()
    receipt = _receipt(record)
    assert verify_a1_hidden_acceptance(
        record, receipt, expected_candidate_artifact_hash="d" * 64
    ) == receipt


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"case_set_id": "OTHER"}, "case_set_id"),
        ({"commitment_hash": "e" * 64}, "commitment"),
        ({"candidate_artifact_hash": "e" * 64}, "candidate artifact"),
        ({"status": "fail"}, "did not pass"),
        ({"use_number": 3}, "max 2"),
        ({"failure_classes": ("same_bar_fill",)}, "failure classes"),
    ],
)
def test_verifier_fails_closed_on_identity_status_budget_or_failure_drift(mutation, message):
    record = _record()
    receipt = _receipt(record)
    values = {
        "case_set_id": receipt.case_set_id,
        "commitment_hash": receipt.commitment_hash,
        "candidate_artifact_hash": receipt.candidate_artifact_hash,
        "status": receipt.status,
        "aggregate_metrics": receipt.aggregate_metrics,
        "failure_classes": receipt.failure_classes,
        "use_number": receipt.use_number,
    }
    values.update(mutation)
    changed = SafeAcceptanceReceipt(**values)
    with pytest.raises(A1HiddenAcceptanceError, match=message):
        verify_a1_hidden_acceptance(
            record, changed, expected_candidate_artifact_hash="d" * 64
        )


def test_loaders_reject_extra_fields_that_could_leak_sealed_material(tmp_path):
    record = _record()
    seal_path = tmp_path / "seal.json"
    seal_payload = {
        "case_set_id": record.case_set_id,
        "case_merkle_root": record.case_merkle_root,
        "labels_hash": record.labels_hash,
        "sealed_at": record.sealed_at,
        "eval_harness_sha": record.eval_harness_sha,
        "scorecard_ref": record.scorecard_ref,
        "max_uses": record.max_uses,
        "raw_cases": ["forbidden"],
    }
    seal_path.write_text(json.dumps(seal_payload), encoding="utf-8")
    with pytest.raises(A1HiddenAcceptanceError, match="extra=.*raw_cases"):
        load_seal_record(seal_path)

    receipt = _receipt(record)
    receipt_path = tmp_path / "receipt.json"
    receipt_payload = {
        "case_set_id": receipt.case_set_id,
        "commitment_hash": receipt.commitment_hash,
        "candidate_artifact_hash": receipt.candidate_artifact_hash,
        "status": receipt.status,
        "aggregate_metrics": [["score", 1.0]],
        "failure_classes": [],
        "use_number": receipt.use_number,
        "labels": ["forbidden"],
    }
    receipt_path.write_text(json.dumps(receipt_payload), encoding="utf-8")
    with pytest.raises(A1HiddenAcceptanceError, match="extra=.*labels"):
        load_safe_receipt(receipt_path)


def test_safe_receipt_loader_rejects_duplicate_or_nonfinite_metrics(tmp_path):
    record = _record()
    receipt = _receipt(record)
    base = {
        "case_set_id": receipt.case_set_id,
        "commitment_hash": receipt.commitment_hash,
        "candidate_artifact_hash": receipt.candidate_artifact_hash,
        "status": receipt.status,
        "failure_classes": [],
        "use_number": receipt.use_number,
    }
    path = tmp_path / "receipt.json"

    path.write_text(json.dumps({**base, "aggregate_metrics": [["score", 1.0], ["score", 1.0]]}), encoding="utf-8")
    with pytest.raises(A1HiddenAcceptanceError, match="duplicate aggregate metric"):
        load_safe_receipt(path)

    path.write_text('{"case_set_id":"A1-EXECUTION-HIDDEN","commitment_hash":"' + record.commitment_hash + '","candidate_artifact_hash":"' + ('d' * 64) + '","status":"pass","aggregate_metrics":[["score",NaN]],"failure_classes":[],"use_number":1}', encoding="utf-8")
    with pytest.raises(A1HiddenAcceptanceError, match="must be finite"):
        load_safe_receipt(path)
