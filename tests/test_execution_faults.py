from __future__ import annotations

import copy

import pytest

from finance_quant.execution.conformance import canonical_receipt_hash, load_runtime_contract
from finance_quant.execution.reference import (
    ReferenceExecutionError,
    restart_daily_reference_from_checkpoint,
    run_daily_reference,
)


def _fixture() -> dict:
    return {
        "fixture_id": "daily-fault-001",
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


def _checkpoint_fixture(full: dict, committed_event_count: int) -> dict:
    checkpoint = copy.deepcopy(full)
    checkpoint["events"] = checkpoint["events"][:committed_event_count]
    if committed_event_count == 0:
        checkpoint["intents"] = []
    else:
        boundary_time = checkpoint["events"][-1]["event_time"]
        checkpoint["intents"] = [
            intent for intent in checkpoint["intents"] if intent["created_at"] <= boundary_time
        ]
    return checkpoint


def _authoritative_state(receipt: dict) -> dict:
    return {
        key: receipt[key]
        for key in (
            "orders",
            "fills",
            "cash_ledger",
            "positions",
            "corporate_actions",
            "rejections",
            "faults",
            "cash",
            "equity",
            "nav",
            "realized_pnl",
            "unrealized_pnl",
        )
    }


def test_fq_prop_022_restart_from_committed_boundary_converges() -> None:
    contract = load_runtime_contract()
    fixture = _fixture()
    checkpoint = run_daily_reference(_checkpoint_fixture(fixture, 2), contract, seed=17)
    uninterrupted = run_daily_reference(fixture, contract, seed=17)

    restarted = restart_daily_reference_from_checkpoint(fixture, contract, checkpoint, seed=17)

    assert _authoritative_state(restarted) == _authoritative_state(uninterrupted)
    assert restarted["input_hash"] == uninterrupted["input_hash"]
    assert restarted["replay_lineage"]["parent_receipt_hash"] == checkpoint["receipt_hash"]
    assert restarted["replay_lineage"]["committed_event_count"] == len(fixture["events"])


def test_fq_prop_022_corrupted_checkpoint_hash_fails_closed() -> None:
    contract = load_runtime_contract()
    fixture = _fixture()
    checkpoint = run_daily_reference(_checkpoint_fixture(fixture, 2), contract, seed=17)
    checkpoint["cash"] = "999999"

    with pytest.raises(ReferenceExecutionError, match="receipt_hash mismatch"):
        restart_daily_reference_from_checkpoint(fixture, contract, checkpoint, seed=17)


def test_fq_prop_022_rehashed_checkpoint_state_corruption_still_fails_closed() -> None:
    contract = load_runtime_contract()
    fixture = _fixture()
    checkpoint = run_daily_reference(_checkpoint_fixture(fixture, 2), contract, seed=17)
    checkpoint["cash"] = "999999"
    checkpoint["receipt_hash"] = canonical_receipt_hash(checkpoint, contract)

    with pytest.raises(ReferenceExecutionError, match="does not match committed fixture boundary"):
        restart_daily_reference_from_checkpoint(fixture, contract, checkpoint, seed=17)


def test_fq_prop_022_invalid_committed_boundary_fails_closed() -> None:
    contract = load_runtime_contract()
    fixture = _fixture()
    checkpoint = run_daily_reference(_checkpoint_fixture(fixture, 2), contract, seed=17)
    checkpoint["replay_lineage"]["committed_event_count"] = 99
    checkpoint["receipt_hash"] = canonical_receipt_hash(checkpoint, contract)

    with pytest.raises(ReferenceExecutionError, match="exceeds fixture"):
        restart_daily_reference_from_checkpoint(fixture, contract, checkpoint, seed=17)


def test_fq_prop_022_checkpoint_seed_mismatch_fails_closed() -> None:
    contract = load_runtime_contract()
    fixture = _fixture()
    checkpoint = run_daily_reference(_checkpoint_fixture(fixture, 2), contract, seed=17)

    with pytest.raises(ReferenceExecutionError, match="seed mismatch"):
        restart_daily_reference_from_checkpoint(fixture, contract, checkpoint, seed=18)
