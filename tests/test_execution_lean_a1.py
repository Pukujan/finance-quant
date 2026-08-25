import pytest

from finance_quant.execution.conformance import load_runtime_contract
from finance_quant.execution.lean_a1 import LeanA1AdapterError, normalize_lean_daily_result
from finance_quant.execution.reference import run_daily_reference


def _fixture():
    return {
        "fixture_id": "lean-a1-smoke",
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
                "order_id": "order-1",
                "intent_id": "intent-1",
                "status": "Filled",
                "quantity": "5",
                "filled_quantity": "5",
            }
        ],
        "fills": [
            {
                "fill_id": "fill-1",
                "order_id": "order-1",
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
        "cash_ledger": [{"entry_id": "cash:fill-1", "kind": "FILL", "amount": "-60"}],
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


def test_lean_adapter_normalizes_only_shared_daily_subset():
    contract = load_runtime_contract()
    receipt = normalize_lean_daily_result(_lean_result(), _fixture(), contract)
    assert receipt["runtime"] == "lean"
    assert receipt["orders"][0]["state"] == "FILLED"
    assert receipt["fills"][0]["source_event_id"] == "bar-2"
    assert receipt["receipt_hash"]


def test_lean_adapter_uses_same_normalized_fixture_identity_as_reference():
    contract = load_runtime_contract()
    fixture = _fixture()
    reference = run_daily_reference(fixture, contract)
    candidate = normalize_lean_daily_result(_lean_result(), fixture, contract)
    assert candidate["input_hash"] == reference["input_hash"]


def test_lean_adapter_rejects_same_bar_fill():
    contract = load_runtime_contract()
    raw = _lean_result()
    raw["fills"][0]["source_event_id"] = "bar-1"
    raw["fills"][0]["event_time"] = "2026-01-01T00:00:00Z"
    with pytest.raises(LeanA1AdapterError, match="FQ-PROP-015"):
        normalize_lean_daily_result(raw, _fixture(), contract)


def test_lean_adapter_rejects_future_known_fill_source():
    contract = load_runtime_contract()
    fixture = _fixture()
    fixture["events"][1]["known_at"] = "2026-01-03T00:00:00Z"
    with pytest.raises(LeanA1AdapterError, match="future-known"):
        normalize_lean_daily_result(_lean_result(), fixture, contract)


def test_lean_adapter_rejects_unknown_native_status():
    contract = load_runtime_contract()
    raw = _lean_result()
    raw["orders"][0]["status"] = "UpdateSubmitted"
    with pytest.raises(LeanA1AdapterError, match="unsupported LEAN order status"):
        normalize_lean_daily_result(raw, _fixture(), contract)


def test_lean_adapter_rejects_ambiguous_fill_lineage():
    contract = load_runtime_contract()
    raw = _lean_result()
    raw["fills"][0]["intent_id"] = "other-intent"
    with pytest.raises(LeanA1AdapterError, match="lineage is ambiguous"):
        normalize_lean_daily_result(raw, _fixture(), contract)
