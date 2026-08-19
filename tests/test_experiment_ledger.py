from __future__ import annotations

import pytest

from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec, RunStatus


def spec() -> RunSpec:
    return RunSpec("B1", "c" * 40, "e" * 64, "d" * 64, "f" * 64, "m" * 64,
                   (42,), "walk-forward-v0", "cost-v0")


def test_run_is_idempotent_and_terminal_record_is_immutable(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    first, duplicate = ledger.begin(spec()), ledger.begin(spec())
    assert first.run_id == duplicate.run_id and first.status is RunStatus.RUNNING
    done = ledger.finalize(first.run_id, RunStatus.SUCCESS, {"rank_ic": 0.1}, {"model": "sha"})
    assert ledger.finalize(first.run_id, RunStatus.SUCCESS, {"rank_ic": 0.1}) == done
    with pytest.raises(LedgerError):
        ledger.finalize(first.run_id, RunStatus.SUCCESS, {"rank_ic": 0.9})
    ledger.close()


def test_failed_run_remains_visible(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    r = ledger.begin(spec())
    failed = ledger.finalize(r.run_id, RunStatus.FAILED, error_class="RuntimeError")
    assert ledger.get(r.run_id) == failed
    ledger.close()
