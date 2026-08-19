from finance_quant.lineage.evidence import EvidenceCommit
from finance_quant.lineage.pack import LocalEvidencePack


def test_local_evidence_pack_writes_hash_named_json(tmp_path):
    pack = LocalEvidencePack(tmp_path / "pack")
    commit = EvidenceCommit("RunRecord", "run-1", "ExperimentRun", "2026-08-19", ("snap",))
    path = pack.commit(commit)
    assert path.exists()
    assert commit.hash in pack.list_hashes()
    text = path.read_text(encoding="utf-8")
    assert "ExperimentRun" in text
    assert "numeric" not in text
