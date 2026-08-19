import json

from finance_quant.acceptance.mini_set import make_mini_set_commitment, write_mini_set_receipt


def test_mini_set_commitment_and_receipt_publish_merkle_only(tmp_path):
    case_a = "case-a-secret-payload"
    case_b = "case-b-secret-payload"
    labels = "labels-secret-payload"
    case_hashes = [_hash_only(case_a), _hash_only(case_b)]
    seal = make_mini_set_commitment(case_hashes, _hash_only(labels), "h" * 40, max_uses=2)
    receipt_path = write_mini_set_receipt(seal, "candidate", {"score": 1.0}, [], tmp_path / "mini.json")
    text = receipt_path.read_text()
    # Raw case and label payloads must never appear in the public receipt.
    assert case_a not in text
    assert case_b not in text
    assert labels not in text
    # Merkle root and labels_hash are present as keys with hex values.
    parsed = json.loads(text)
    assert set(parsed.keys()) == {
        "aggregate_metrics", "candidate_artifact_hash", "case_merkle_root",
        "case_set_id", "commitment_hash", "failure_classes", "labels_hash",
        "status", "use_number",
    }
    assert parsed["case_merkle_root"] == seal.case_merkle_root
    assert parsed["labels_hash"] == seal.labels_hash


def _hash_only(value: str) -> str:
    import hashlib, json
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
