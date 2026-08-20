"""Failure-drill coverage for the append-only experiment ledger facade."""
from __future__ import annotations

import json

import pytest

from finance_quant.experiments.ledger import ExperimentLedger, LedgerError, RunSpec, RunStatus


def _spec(experiment_id: str) -> RunSpec:
    return RunSpec(
        experiment_id, "c" * 40, "e" * 64, "d" * 64, "f" * 64, "m" * 64,
        (42,), "walk-forward-v0", "cost-v0",
    )


@pytest.mark.parametrize(
    ("experiment_id", "error_class", "partial_metrics"),
    [
        ("failed-mid-training", "TrainingStepError", {"epoch": 3.0, "loss": 0.42}),
        ("failed-mid-backtest", "BacktestExecutionError", {"completed_windows": 2.0}),
    ],
)
def test_failed_run_drill_preserves_queryable_failure_and_audit_event(
    tmp_path, experiment_id, error_class, partial_metrics,
):
    audit_path = tmp_path / "runs.jsonl"
    ledger = ExperimentLedger(tmp_path / "runs.db", audit_path)
    started = ledger.begin(_spec(experiment_id))

    # This represents the exception handler reached after training/backtesting starts.
    failed = ledger.finalize(
        started.run_id, RunStatus.FAILED, metrics=partial_metrics, error_class=error_class,
    )

    assert ledger.get(started.run_id) == failed
    assert failed.status is RunStatus.FAILED
    assert failed.error_class == error_class
    assert failed.metrics == tuple(sorted(partial_metrics.items()))

    audit_events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert {
        "event": "finalize",
        "run_id": started.run_id,
        "status": "failed",
        "experiment_id": experiment_id,
        "error_class": error_class,
    } in audit_events
    ledger.close()


def test_terminal_failed_run_is_immutable_and_facade_has_no_delete_api(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    started = ledger.begin(_spec("immutable-failure"))
    ledger.finalize(
        started.run_id, RunStatus.FAILED, metrics={"epoch": 3.0}, error_class="TrainingStepError",
    )

    with pytest.raises(LedgerError, match="immutable"):
        ledger.finalize(started.run_id, RunStatus.INVALID, metrics={"epoch": 4.0})
    assert not hasattr(ledger, "delete")
    ledger.close()
