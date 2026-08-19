from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_failed_and_invalid_are_distinct_terminal_states(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    a = ledger.begin(RunSpec("a", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost"))
    b = ledger.begin(RunSpec("b", "c" * 40, "env", "data", "ir", "model", (2,), "split", "cost"))
    fa = ledger.finalize(a.run_id, RunStatus.FAILED, error_class="Boom")
    ib = ledger.finalize(b.run_id, RunStatus.INVALID, error_class="TemporalError")
    assert fa.status is RunStatus.FAILED
    assert ib.status is RunStatus.INVALID
    ledger.close()
