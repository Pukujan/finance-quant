from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_jsonl_audit_mirror_appends_begin_and_finalize(tmp_path):
    db = tmp_path / "runs.db"
    jsonl = tmp_path / "runs.jsonl"
    ledger = ExperimentLedger(db, jsonl)
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    lines = jsonl.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert '"event": "begin"' in lines[0]
    assert '"event": "finalize"' in lines[1]
    ledger.close()
