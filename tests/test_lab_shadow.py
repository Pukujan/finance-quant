from __future__ import annotations

import pytest

from finance_quant.lab.core import LabError
from finance_quant.lab.shadow import ShadowPaperLab


T0 = "2024-01-02T16:00:00+00:00"
T1 = "2024-01-03T14:30:00+00:00"
T2 = "2024-01-04T14:30:00+00:00"


def test_shadow_accounts_are_isolated_restartable_and_idempotent(tmp_path):
    lab = ShadowPaperLab(tmp_path, initial_cash=100_000)

    a = lab.advance(
        arm_id="A-price",
        instrument="AAA",
        decision_time=T0,
        execution_time=T1,
        predicted_return=0.01,
        execution_price=100,
    )
    b = lab.advance(
        arm_id="B-news",
        instrument="AAA",
        decision_time=T0,
        execution_time=T1,
        predicted_return=-0.01,
        execution_price=100,
    )

    assert a["position"] == "950"
    assert len(a["state"]["fills"]) == 1
    assert b["position"] == "0"
    assert len(b["state"]["fills"]) == 0
    assert b["nav"]["nav"] == "100000"

    # New object simulates a process restart. Existing account cash must not be reset.
    restarted = ShadowPaperLab(tmp_path, initial_cash=100_000)
    rerun = restarted.advance(
        arm_id="A-price",
        instrument="AAA",
        decision_time=T0,
        execution_time=T1,
        predicted_return=0.01,
        execution_price=100,
    )
    assert rerun["position"] == "950"
    assert len(rerun["state"]["fills"]) == 1
    assert rerun["executed"] is False

    # A later negative signal closes only A; B remains untouched.
    closed = restarted.advance(
        arm_id="A-price",
        instrument="AAA",
        decision_time=T1,
        execution_time=T2,
        predicted_return=-0.01,
        execution_price=110,
    )
    assert closed["position"] == "0"
    assert len(closed["state"]["fills"]) == 2
    b_after = restarted.snapshot("B-news", {})
    assert len(b_after["state"]["fills"]) == 0
    assert b_after["nav"]["nav"] == "100000"


def test_shadow_account_requires_marks_for_other_open_positions(tmp_path):
    lab = ShadowPaperLab(tmp_path)
    lab.advance(
        arm_id="multi",
        instrument="AAA",
        decision_time=T0,
        execution_time=T1,
        predicted_return=0.01,
        execution_price=100,
        target_allocation=0.4,
    )

    with pytest.raises(LabError, match="missing mark"):
        lab.advance(
            arm_id="multi",
            instrument="BBB",
            decision_time=T1,
            execution_time=T2,
            predicted_return=0.01,
            execution_price=50,
            target_allocation=0.4,
        )

    result = lab.advance(
        arm_id="multi",
        instrument="BBB",
        decision_time=T1,
        execution_time=T2,
        predicted_return=0.01,
        execution_price=50,
        target_allocation=0.4,
        marks={"AAA": 105},
    )
    assert result["position"] != "0"
