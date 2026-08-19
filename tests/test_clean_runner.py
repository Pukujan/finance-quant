from pathlib import Path

from finance_quant.acceptance.clean_runner import score_public_mini_set
from finance_quant.orchestration.contracts import content_hash


def test_clean_runner_writes_aggregate_receipt_without_payloads(tmp_path):
    hashes = [content_hash(f"secret-{i}") for i in range(4)]
    out = score_public_mini_set("cand", hashes, content_hash("labs"), {"score": 0.1}, [],
                                tmp_path / "receipt.json")
    text = out.read_text(encoding="utf-8")
    assert "secret-" not in text
    assert "labs" not in text
    assert "commitment_hash" in text
