from __future__ import annotations

import copy

import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.reference import ReferenceExecutionError, run_daily_reference


def _fixture() -> dict:
    return {
        "fixture_id": "daily-basic-001",
        "initial_cash": "1000",
        "fee_per_unit": "0.10",
        "events": [
            {
                "event_id": "bar-1",
                "instrument_id": "TEST",
                "event_time": "2026-01-02T16:00:00Z",
                "known_at": "2026-01-02T16:00:00Z",
                "sequence": 1,
                "payload": {"open": "10", "close": "11", "liquidity": "100"},
            },
            {
                "event_id": "bar-2",
                "instrument_id": "TEST",
                "event_time": "2026-01-05T16:00:00Z",
                "known_at": "2026-01-05T16:00:00Z",
                "sequence": 2,
                "payload": {"open": "12", "close": "13", "liquidity": "3"},
            },
            {
                "event_id": "bar-3",
                "instrument_id": "TEST",
                "event_time": "2026-01-06T16:00:00Z",
                "known_at": "2026-01-06T16:00:00Z",
                "sequence": 3,
                "payload": {"open": "14", "close": "15", "liquidity": "100"},
            },
        ],
        "intents": [
            {
                "intent_id": "intent-1",
                "instrument_id": "TEST",
                "created_at": "2026-01-02T16:00:00Z",
                "side": "BUY",
                "quantity": "5",
                "order_type": "MARKET",
            }
        ],
    }


def test_fq_prop_015_daily_decision_never_fills_same_bar() -> None:
    receipt = run_daily_reference(_fixture(), load_runtime_contract())
    assert receipt["fills"][0]["source_event_id"] == "bar-2"
    assert receipt["fills"][0]["event_time"] > _fixture()["intents"][0]["created_at"]


def test_fq_prop_016_partial_fill_never_exceeds_order_quantity() -> None:
    receipt = run_daily_reference(_fixture(), load_runtime_contract())
    order = receipt["orders"][0]
    assert order["state"] == "PARTIALLY_FILLED"
    assert float(order["filled_quantity"]) <= float(order["quantity"])


def test_fq_prop_017_reference_accounting_reconciles_cash_equity_and_nav() -> None:
    receipt = run_daily_reference(_fixture(), load_runtime_contract())
    assert receipt["cash"] == "963.70"
    assert receipt["equity"] == "45"
    assert receipt["nav"] == "1008.70"


def test_fq_prop_018_exact_duplicate_event_is_idempotent() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    duplicated = copy.deepcopy(base)
    duplicated["events"].append(copy.deepcopy(duplicated["events"][1]))
    assert run_daily_reference(base, contract) == run_daily_reference(duplicated, contract)


def test_ambiguous_duplicate_event_identity_fails_closed() -> None:
    fixture = _fixture()
    conflicting = copy.deepcopy(fixture["events"][1])
    conflicting["payload"]["open"] = "999"
    fixture["events"].append(conflicting)
    with pytest.raises(ReferenceExecutionError, match="ambiguous duplicate"):
        run_daily_reference(fixture, load_runtime_contract())


def test_fq_prop_019_future_known_event_does_not_influence_earlier_execution() -> None:
    contract = load_runtime_contract()
    base = _fixture()
    poisoned = copy.deepcopy(base)
    poisoned["events"].insert(
        1,
        {
            "event_id": "future-known-poison",
            "instrument_id": "TEST",
            "event_time": "2026-01-03T16:00:00Z",
            "known_at": "2026-02-01T16:00:00Z",
            "sequence": 9,
            "payload": {"open": "1", "close": "1", "liquidity": "1000"},
        },
    )
    base_receipt = run_daily_reference(base, contract)
    poisoned_receipt = run_daily_reference(poisoned, contract)
    assert base_receipt["fills"] == poisoned_receipt["fills"]
    assert base_receipt["cash"] == poisoned_receipt["cash"]
    assert base_receipt["positions"] == poisoned_receipt["positions"]


def test_fq_prop_020_reference_receipt_is_deterministic_across_three_runs() -> None:
    contract = load_runtime_contract()
    receipts = [run_daily_reference(_fixture(), contract, seed=11) for _ in range(3)]
    assert receipts[0] == receipts[1] == receipts[2]


def test_zero_liquidity_cannot_synthesize_fill() -> None:
    fixture = _fixture()
    for event in fixture["events"][1:]:
        event["payload"]["liquidity"] = "0"
    receipt = run_daily_reference(fixture, load_runtime_contract())
    assert receipt["fills"] == []
    assert receipt["orders"][0]["state"] == "REJECTED"
