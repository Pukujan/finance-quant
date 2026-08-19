import json
from pathlib import Path

from finance_quant.acceptance.mini_set import make_mini_set_commitment
from finance_quant.orchestration.contracts import content_hash


def test_public_seal_mini_a_is_reproducible():
    case_hashes = [content_hash(f"mini-case-{i}") for i in range(8)]
    labels_hash = content_hash("labels-not-in-this-repo")
    expected = make_mini_set_commitment(case_hashes, labels_hash, "h" * 40, max_uses=2)

    path = Path("docs/acceptance/SEAL_MINI_A.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["case_set_id"] == expected.case_set_id
    assert data["commitment_hash"] == expected.commitment_hash
    assert data["case_merkle_root"] == expected.case_merkle_root
    assert data["labels_hash"] == expected.labels_hash
    assert data["max_uses"] == expected.max_uses
