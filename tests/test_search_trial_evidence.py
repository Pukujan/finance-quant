from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.lineage.pack import LocalEvidencePack
from finance_quant.lineage.runs import evidence_commit_for_run


def test_search_trial_evidence_uses_search_activity(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    pack = LocalEvidencePack(tmp_path / "pack")
    spec = RunSpec("random-v0-x", "c" * 40, "env", "snap", "ir", "none", (1,), "split", "cost",
                   agent_origin="random-v0")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"score": 1.0})
    commit = evidence_commit_for_run(done, "snap", "SearchTrial")
    pack.commit(commit)
    assert commit.activity_type == "SearchTrial"
    assert len(pack.list_hashes()) == 1
    ledger.close()
