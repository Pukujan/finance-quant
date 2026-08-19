import pytest

from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec, RunStatus


def test_failed_trial_cannot_be_deleted(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("fail", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    failed = ledger.finalize(run.run_id, RunStatus.FAILED, error_class="Boom")
    assert ledger.get(run.run_id).status is RunStatus.FAILED
    assert not hasattr(ledger, "delete")
    with pytest.raises(LedgerError):
        ledger.finalize(run.run_id, RunStatus.SUCCESS, {"ic": 1.0})
    ledger.close()
    assert failed.error_class == "Boom"
