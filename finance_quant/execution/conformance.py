"""A1 execution/runtime conformance helpers.

This module validates finance-quant-owned contracts and normalizes candidate-runtime
receipts. It contains no runtime adapter and grants no trading authority.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT_PATH = ROOT / "contracts" / "execution" / "runtime-conformance-v1.json"
EXPECTED_PROPERTY_IDS = {f"FQ-PROP-{i:03d}" for i in range(15, 23)}


class ConformanceError(ValueError):
    """Raised when an A1 contract or normalized receipt fails closed."""


def load_runtime_contract(path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_runtime_contract(contract: Mapping[str, Any]) -> None:
    errors: list[str] = []
    if contract.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if contract.get("issue") != 15 or contract.get("phase") != "A1":
        errors.append("runtime contract must remain bound to issue #15 / A1")

    authority = contract.get("authority", {})
    expected_authority = {
        "trading": "NONE",
        "paper_trading": "DISABLED",
        "live_capital": "DISABLED",
        "sealed_holdout_access": "DENIED_TO_ORDINARY_AGENTS",
    }
    for key, value in expected_authority.items():
        if authority.get(key) != value:
            errors.append(f"authority.{key} must remain {value}")

    if contract.get("event_order") != ["event_time", "sequence", "event_id"]:
        errors.append("event_order must be deterministic event_time/sequence/event_id")
    if contract.get("minimum_repeated_runs", 0) < 3:
        errors.append("A1 requires at least three repeated deterministic runs")
    if contract.get("comparison", {}).get("default_for_unlisted_semantic_difference") != "FAIL":
        errors.append("unlisted semantic differences must fail closed")

    props = contract.get("properties", [])
    prop_ids = [p.get("property_id") for p in props]
    if len(prop_ids) != len(set(prop_ids)):
        errors.append("runtime contract property IDs must be unique")
    if set(prop_ids) != EXPECTED_PROPERTY_IDS:
        errors.append(f"runtime contract must define exactly {sorted(EXPECTED_PROPERTY_IDS)}")

    receipt = contract.get("receipt", {})
    required = receipt.get("required_top_level", [])
    if not required or len(required) != len(set(required)):
        errors.append("receipt.required_top_level must be a non-empty unique list")
    for field in ("contract_version", "runtime", "runtime_version", "input_hash", "receipt_hash", "replay_lineage"):
        if field not in required:
            errors.append(f"receipt.required_top_level missing {field}")
    if receipt.get("deterministic_key_order") is not True:
        errors.append("receipt normalization must require deterministic key order")

    if errors:
        raise ConformanceError("; ".join(errors))


def _find_forbidden_keys(value: Any, forbidden: set[str], path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in forbidden:
                found.append(child_path)
            found.extend(_find_forbidden_keys(child, forbidden, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_find_forbidden_keys(child, forbidden, f"{path}[{index}]"))
    return found


def validate_receipt(receipt: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    validate_runtime_contract(contract)
    errors: list[str] = []
    receipt_contract = contract["receipt"]
    missing = [field for field in receipt_contract["required_top_level"] if field not in receipt]
    if missing:
        errors.append(f"missing required receipt fields: {missing}")

    forbidden = set(receipt_contract.get("forbidden_identity_inputs", []))
    found = _find_forbidden_keys(receipt, forbidden)
    if found:
        errors.append(f"forbidden identity inputs present: {found}")

    allowed_states = set(contract.get("normalized_order_states", []))
    for index, order in enumerate(receipt.get("orders", [])):
        state = order.get("state") if isinstance(order, Mapping) else None
        if state not in allowed_states:
            errors.append(f"orders[{index}].state is not normalized: {state!r}")

    if receipt.get("contract_version") != contract.get("schema_version"):
        errors.append("receipt contract_version must equal runtime contract schema_version")

    if errors:
        raise ConformanceError("; ".join(errors))


def canonical_receipt_payload(receipt: Mapping[str, Any], contract: Mapping[str, Any]) -> bytes:
    """Return the canonical hash payload, excluding the self-referential receipt hash."""
    validate_receipt(receipt, contract)
    normalized = deepcopy(dict(receipt))
    normalized.pop("receipt_hash", None)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_receipt_hash(receipt: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_receipt_payload(receipt, contract)).hexdigest()
