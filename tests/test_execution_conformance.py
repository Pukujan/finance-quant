from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from finance_quant.execution.conformance import (
    ConformanceError,
    canonical_receipt_hash,
    canonical_receipt_payload,
    load_runtime_contract,
    validate_receipt,
    validate_runtime_contract,
)

ROOT = Path(__file__).resolve().parents[1]


def _receipt() -> dict:
    return {
        "contract_version": "1.0.0",
        "fixture_id": "fixture-basic-001",
        "runtime": "reference",
        "runtime_version": "0",
        "seed": 7,
        "status": "COMPLETE",
        "orders": [{"order_id": "o1", "state": "FILLED", "quantity": "2"}],
        "fills": [{"fill_id": "f1", "order_id": "o1", "quantity": "2", "price": "10.00"}],
        "cash_ledger": [{"kind": "fill", "amount": "-20.00"}],
        "positions": [{"symbol": "TEST", "quantity": "2"}],
        "corporate_actions": [],
        "rejections": [],
        "faults": [],
        "cash": "80.00",
        "equity": "20.00",
        "nav": "100.00",
        "realized_pnl": "0.00",
        "unrealized_pnl": "0.00",
        "input_hash": "input-abc",
        "receipt_hash": "placeholder",
        "replay_lineage": {"parent_receipt_hash": None, "committed_event_count": 2},
    }


def test_runtime_contract_is_bound_to_a1_and_fails_closed() -> None:
    contract = load_runtime_contract()
    validate_runtime_contract(contract)

    mutated = copy.deepcopy(contract)
    mutated["authority"]["paper_trading"] = "ENABLED"
    with pytest.raises(ConformanceError, match="paper_trading"):
        validate_runtime_contract(mutated)


def test_runtime_contract_defines_exact_a1_property_ids() -> None:
    contract = load_runtime_contract()
    ids = {item["property_id"] for item in contract["properties"]}
    assert ids == {f"FQ-PROP-{i:03d}" for i in range(15, 23)}


def test_canonical_receipt_hash_is_independent_of_mapping_key_order_and_self_hash() -> None:
    contract = load_runtime_contract()
    original = _receipt()
    reordered = json.loads(json.dumps(original, sort_keys=True))
    reordered["receipt_hash"] = "different-placeholder"

    assert canonical_receipt_payload(original, contract) == canonical_receipt_payload(reordered, contract)
    assert canonical_receipt_hash(original, contract) == canonical_receipt_hash(reordered, contract)


def test_receipt_missing_required_field_fails_closed() -> None:
    contract = load_runtime_contract()
    receipt = _receipt()
    del receipt["input_hash"]
    with pytest.raises(ConformanceError, match="missing required receipt fields"):
        validate_receipt(receipt, contract)


def test_receipt_forbidden_identity_input_is_rejected_at_any_depth() -> None:
    contract = load_runtime_contract()
    receipt = _receipt()
    receipt["replay_lineage"]["absolute_path"] = "/tmp/machine-specific"
    with pytest.raises(ConformanceError, match="forbidden identity inputs"):
        validate_receipt(receipt, contract)


def test_receipt_rejects_runtime_specific_order_state() -> None:
    contract = load_runtime_contract()
    receipt = _receipt()
    receipt["orders"][0]["state"] = "BROKER_PENDING_INTERNAL"
    with pytest.raises(ConformanceError, match="not normalized"):
        validate_receipt(receipt, contract)


def test_property_catalog_binds_a1_properties_to_executable_oracles() -> None:
    catalog = json.loads((ROOT / "contracts" / "properties" / "finance-quant-properties-v1.json").read_text())
    by_id = {item["property_id"]: item for item in catalog["properties"]}
    for number in range(15, 23):
        prop = by_id[f"FQ-PROP-{number:03d}"]
        assert prop["status"] == "active"
        assert prop["oracle"]
        for oracle in prop["oracle"]:
            path = oracle.split("::", 1)[0]
            assert (ROOT / path).is_file(), oracle
