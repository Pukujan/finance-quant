from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec
import pytest


def test_run_spec_requires_seeds_and_hashes():
    with pytest.raises(LedgerError):
        RunSpec("e", "", "env", "data", "ir", "model", (1,), "split", "cost")
    with pytest.raises(LedgerError):
        RunSpec("e", "c" * 40, "env", "data", "ir", "model", (), "split", "cost")
    ledger = ExperimentLedger("unused.db") if False else None
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1, 2), "split", "cost")
    assert spec.idempotency_key
