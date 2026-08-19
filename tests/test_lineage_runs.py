from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.lineage.runs import evidence_for_run


def test_b1_run_emits_cold_path_evidence_without_numeric_payload(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("B1", "c" * 40, "env", "snap", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"n": 1.0})
    payload = evidence_for_run(done, "snap")
    assert payload["entity_type"] == "RunRecord"
    assert tuple(payload["derived_from"]) == ("snap", "ir")
    assert "n" not in str(payload["hash"])
    ledger.close()
