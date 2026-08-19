from finance_quant.lineage.evidence import EvidenceCommit
from finance_quant.lineage.pack import LocalEvidencePack


def test_evidence_commit_hash_is_deterministic():
    commit = EvidenceCommit("RunRecord", "a" * 64, "ExperimentRun", "2024-01-01",
                            derived_from=("b" * 64,), decided_by="owner")
    h1 = commit.hash
    h2 = EvidenceCommit("RunRecord", "a" * 64, "ExperimentRun", "2024-01-01",
                        derived_from=("b" * 64,), decided_by="owner").hash
    assert h1 == h2


def test_local_pack_roundtrip(tmp_path):
    pack = LocalEvidencePack(tmp_path / "pack")
    commit = EvidenceCommit("FeatureIR", "c" * 64, "SearchTrial", "2024-01-02")
    path = pack.commit(commit)
    assert path.exists()
    assert commit.hash in pack.list_hashes()
