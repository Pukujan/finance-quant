from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec, RunStatus
import pytest


def test_cannot_finalize_as_running(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    with pytest.raises(LedgerError):
        ledger.finalize(run.run_id, RunStatus.RUNNING)
    ledger.close()
