from finance_quant.lineage.evidence import EvidenceCommit, evidence_payload
from finance_quant.lineage.graph import STATIC_FIXTURE, as_of_edges


def test_late_announced_graph_edge_is_excluded_as_of_earlier_knowledge_time():
    early = as_of_edges(STATIC_FIXTURE, "2024-02-01", "2024-02-01")
    late = as_of_edges(STATIC_FIXTURE, "2024-04-01", "2024-04-01")
    assert [(e.src, e.dst) for e in early] == [("AAA", "BBB")]
    assert len(late) == 2


def test_evidence_commit_is_hashable_and_cold_path_only():
    commit = EvidenceCommit("RunRecord", "runhash", "ExperimentRun", "2024-03-01", ("snap",))
    payload = evidence_payload(commit)
    assert payload["hash"] == commit.hash
    assert "numeric_values" not in payload
