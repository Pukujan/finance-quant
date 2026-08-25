from copy import deepcopy
from decimal import Decimal

import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.differential import (
    DifferentialConformanceError,
    assert_normalized_receipts_conform,
    compare_normalized_receipts,
)
from finance_quant.execution.lean_a1 import normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference


def _fixture():
    return {
        "fixture_id": "differential-smoke",
        "initial_cash": "1000",
        "fee_per_unit": "1",
        "events": [
            {
                "event_id": "bar-1",
                "instrument_id": "AAA",
                "event_time": "2026-01-01T00:00:00Z",
                "known_at": "2026-01-01T00:00:00Z",
                "sequence": 1,
                "payload": {"open": "10", "close": "10", "liquidity": "10"},
            },
            {
                "event_id": "bar-2",
                "instrument_id": "AAA",
                "event_time": "2026-01-02T00:00:00Z",
                "known_at": "2026-01-02T00:00:00Z",
                "sequence": 2,
                "payload": {"open": "11", "close": "12", "liquidity": "10"},
            },
        ],
        "intents": [
            {
                "intent_id": "intent-1",
                "instrument_id": "AAA",
                "created_at": "2026-01-01T00:00:00Z",
                "side": "BUY",
                "quantity": "5",
                "order_type": "MARKET",
            }
        ],
    }


def _lean_result():
    return {
        "engine": "LEAN",
        "engine_version": "candidate-pin",
        "status": "COMPLETE",
        "orders": [
            {
                "order_id": "lean-order-73",
                "intent_id": "intent-1",
                "status": "Filled",
                "quantity": "5",
                "filled_quantity": "5",
            }
        ],
        "fills": [
            {
                "fill_id": "lean-fill-991",
                "order_id": "lean-order-73",
                "intent_id": "intent-1",
                "instrument_id": "AAA",
                "event_time": "2026-01-02T00:00:00Z",
                "quantity": "5",
                "price": "11",
                "fee": "5",
                "slippage": "0",
                "source_event_id": "bar-2",
            }
        ],
        "cash_ledger": [
            {
                "entry_id": "lean-ledger-1",
                "fill_id": "lean-fill-991",
                "kind": "FILL",
                "amount": "-60",
            }
        ],
        "positions": [{"instrument_id": "AAA", "quantity": "5"}],
        "corporate_actions": [],
        "rejections": [],
        "faults": [],
        "cash": "940",
        "equity": "60",
        "nav": "1000",
        "realized_pnl": "0",
        "unrealized_pnl": "0",
        "replay_lineage": {"parent_receipt_hash": None, "committed_event_count": 2},
    }


def _pair():
    contract = load_runtime_contract()
    fixture = _fixture()
    reference = run_daily_reference(fixture, contract)
    candidate = normalize_lean_daily_result(_lean_result(), fixture, contract)
    return contract, reference, candidate


def test_reference_and_lean_shared_subset_have_no_semantic_differences():
    contract, reference, candidate = _pair()
    assert compare_normalized_receipts(reference, candidate, contract) == []
    assert_normalized_receipts_conform(reference, candidate, contract)


def test_runtime_identity_and_self_hash_are_explicitly_permitted_differences():
    contract, reference, candidate = _pair()
    assert reference["runtime"] != candidate["runtime"]
    assert reference["runtime_version"] != candidate["runtime_version"]
    assert reference["receipt_hash"] != candidate["receipt_hash"]
    assert compare_normalized_receipts(reference, candidate, contract) == []


def test_exact_semantic_drift_is_reported():
    contract, reference, candidate = _pair()
    candidate = deepcopy(candidate)
    candidate["orders"][0]["state"] = "PARTIALLY_FILLED"
    differences = compare_normalized_receipts(reference, candidate, contract)
    assert differences[0].path == "$.orders"
    assert differences[0].field_class == "exact"
    with pytest.raises(DifferentialConformanceError, match=r"\$\.orders"):
        assert_normalized_receipts_conform(reference, candidate, contract)


def test_numeric_difference_obeys_explicit_tolerance_only():
    contract, reference, candidate = _pair()
    candidate = deepcopy(candidate)
    candidate["nav"] = "1000.01"
    differences = compare_normalized_receipts(reference, candidate, contract)
    assert differences[0].path == "$.nav"
    assert differences[0].field_class == "tolerance_bounded"
    assert compare_normalized_receipts(
        reference, candidate, contract, decimal_tolerance=Decimal("0.01")
    ) == []


def test_required_unclassified_field_fails_closed():
    contract, reference, candidate = _pair()
    contract = deepcopy(contract)
    contract["receipt"]["required_top_level"].append("new_semantic_field")
    reference["new_semantic_field"] = "x"
    candidate["new_semantic_field"] = "x"
    with pytest.raises(DifferentialConformanceError, match="lack a comparison class"):
        compare_normalized_receipts(reference, candidate, contract)
