from pathlib import Path
import json


def test_public_seal_mini_a_has_hashes_not_payloads():
    path = Path("docs/acceptance/SEAL_MINI_A.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["case_set_id"] == "SEAL-MINI-A"
    assert data["use_number"] == 1
    text = path.read_text(encoding="utf-8")
    assert "mini-case-" not in text
    assert "labels-not-in-this-repo" not in text
    assert len(data["commitment_hash"]) == 64
