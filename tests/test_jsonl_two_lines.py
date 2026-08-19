from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_jsonl_has_two_lines_for_begin_and_finalize(tmp_path):
    db, jsonl = tmp_path / "runs.db", tmp_path / "audit.jsonl"
    ledger = ExperimentLedger(db, jsonl)
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    ledger.finalize(run.run_id, RunStatus.INVALID, error_class="X")
    assert len(jsonl.read_text(encoding="utf-8").strip().splitlines()) == 2
    ledger.close()
