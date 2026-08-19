from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec, RunStatus
import pytest


def test_cannot_finalize_unknown_run(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    with pytest.raises(LedgerError):
        ledger.finalize("missing", RunStatus.SUCCESS, {"x": 1.0})
    ledger.close()
