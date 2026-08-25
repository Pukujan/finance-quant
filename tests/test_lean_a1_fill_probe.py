import json
from pathlib import Path

import pytest

from scripts.run_lean_a1_fill_probe import build_raw_lean_result, verify_probe

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "execution" / "a1-lean-fill-probe-v1.json"
PIN = ROOT / "contracts" / "execution" / "lean-a1-candidate-pin-v1.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _probe():
    return {
        "engine": "LEAN",
        "probe_scope": "EquityFillModel.MarketOnOpenFill",
        "order_type": "MarketOnOpen",
        "status": "Filled",
        "fill_quantity": "5",
        "fill_price": "11",
        "fill_time": "2026-06-02T13:30:00Z",
        "source_event_id": "bar-2",
        "instrument_id": "AAA",
    }


def test_lean_candidate_pin_is_exact_credential_free_and_non_authoritative():
    pin = _load(PIN)
    assert pin["source_commit"] == "185c691b89f28bd68e48d53c02147415134975f0"
    assert pin["license_spdx"] == "Apache-2.0"
    assert pin["target_framework"] == "net10.0"
    assert pin["credentials_required"] is False
    assert pin["cli_used"] is False
    assert pin["runtime_disposition"] == "PENDING"
    assert pin["authority"]["trading"] == "NONE"
    assert pin["authority"]["live_capital"] == "DISABLED"


def test_synthetic_lean_fill_probe_converges_with_reference_subset():
    evidence = verify_probe(_probe(), _load(FIXTURE), _load(PIN))
    assert evidence["semantic_conformance"] == "PASS"
    assert evidence["runtime_disposition"] == "PENDING"
    assert evidence["authority"] == "NONE"


def test_probe_accounting_is_derived_from_candidate_fill_not_expected_price():
    raw = build_raw_lean_result(_probe(), _load(FIXTURE), _load(PIN))
    assert raw["fills"][0]["price"] == "11"
    assert raw["cash_ledger"][0]["amount"] == "-55"
    assert raw["cash"] == "945"
    assert raw["nav"] == "1005"


def test_probe_rejects_candidate_fill_at_wrong_execution_instant():
    probe = _probe()
    probe["fill_time"] = "2026-06-02T13:31:00Z"
    with pytest.raises(ValueError, match="fill time"):
        verify_probe(probe, _load(FIXTURE), _load(PIN))
