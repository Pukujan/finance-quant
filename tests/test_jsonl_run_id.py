from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_jsonl_audit_contains_run_id(tmp_path):
    db, jsonl = tmp_path / "runs.db", tmp_path / "runs.jsonl"
    ledger = ExperimentLedger(db, jsonl)
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    text = jsonl.read_text(encoding="utf-8")
    assert run.run_id in text
    ledger.close()
