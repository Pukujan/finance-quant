import json

from finance_quant.__main__ import main


def test_seal_mini_cli_writes_public_commitment(tmp_path):
    out = tmp_path / "SEAL_MINI_A.json"
    ret = main(["seal-mini", "--out", str(out)])
    assert ret == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["case_set_id"] == "SEAL-MINI-A"
    assert data["candidate_artifact_hash"] == "no-candidate-yet"
    assert data["status"] == "pass"
    assert data["use_number"] == 1
    assert len(data["case_merkle_root"]) == 64
