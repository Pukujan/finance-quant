import pytest

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.lineage.pack import LocalEvidencePack
from finance_quant.lineage.runs import evidence_commit_for_run


def test_promotion_review_evidence_requires_decided_by_owner(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    pack = LocalEvidencePack(tmp_path / "pack")
    spec = RunSpec("B1", "c" * 40, "env", "snap", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"rank_ic": 0.1})
    # Workers cannot create a PromotionReview evidence commit; only the owner path can.
    from finance_quant.lineage.evidence import OntologyError
    with pytest.raises(OntologyError):
        evidence_commit_for_run(done, "snap", "PromotionReview")
    # Owner-authored PromotionReview is allowed once decided_by is supplied.
    commit = evidence_commit_for_run(done, "snap", "PromotionReview", decided_by="owner")
    assert commit.decided_by == "owner"
    pack.commit(commit)
    assert "PromotionReview" in (tmp_path / "pack" / f"{commit.hash}.json").read_text(encoding="utf-8")
    ledger.close()
