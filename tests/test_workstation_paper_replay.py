from __future__ import annotations

import pytest

from finance_quant.workstation.data import DailyBar
from scripts.run_workstation_paper_replay import replay


def test_historical_replay_uses_next_open_and_is_durable(tmp_path):
    bars = (
        DailyBar("2024-01-01", 100.0, 101.0, 99.0, 100.0, 1.0),
        DailyBar("2024-01-02", 102.0, 103.0, 101.0, 103.0, 1.0),
        DailyBar("2024-01-03", 104.0, 105.0, 103.0, 105.0, 1.0),
    )
    predictions = (
        {"decision_day": "2024-01-01", "outcome_day": "2024-01-02", "predicted": 0.01},
        {"decision_day": "2024-01-02", "outcome_day": "2024-01-03", "predicted": -0.01},
    )
    result = replay(
        "AAPL",
        bars,
        predictions,
        state_path=tmp_path / "aapl.sqlite",
        initial_cash=1_000.0,
        allocation=0.5,
        slippage_bps=0.0,
    )
    assert result["fills"] == 2
    assert result["orders"] == 2
    assert result["final_nav"] == 1_008.0
    assert result["marked_return"] == pytest.approx(0.008)
    assert result["max_drawdown"] == 0.0
    resumed = replay(
        "AAPL",
        bars,
        predictions,
        state_path=tmp_path / "aapl.sqlite",
        initial_cash=1_000.0,
        allocation=0.5,
        slippage_bps=0.0,
    )
    assert resumed["final_nav"] == result["final_nav"]
    assert resumed["state_hash"] == result["state_hash"]
    assert (tmp_path / "aapl.sqlite.checkpoint.json").exists()
