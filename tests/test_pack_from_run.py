from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.lineage.pack import LocalEvidencePack
from finance_quant.lineage.runs import evidence_commit_for_run


def test_campaign_style_evidence_pack_has_one_file_per_run(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    pack = LocalEvidencePack(tmp_path / "pack")
    spec = RunSpec("B1", "c" * 40, "env", "snap", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"rank_ic": 0.2})
    pack.commit(evidence_commit_for_run(done, "snap"))
    assert len(pack.list_hashes()) == 1
    ledger.close()
