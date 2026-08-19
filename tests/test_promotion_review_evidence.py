from finance_quant.lineage.evidence import EvidenceCommit, evidence_payload


def test_promotion_review_is_an_evidence_commit_not_a_worker_write():
    commit = EvidenceCommit(
        "BacktestReceipt", "receipt-hash", "PromotionReview", "2026-08-19",
        derived_from=("run-hash",), decided_by="owner",
    )
    payload = evidence_payload(commit)
    assert payload["activity_type"] == "PromotionReview"
    assert payload["decided_by"] == "owner"
    assert payload["hash"] == commit.hash
