from __future__ import annotations

import json
from pathlib import Path

from scripts.prepare_a2_controlled_fixture import prepare_controlled_fixture
from scripts.run_a2_controlled_campaign import build_campaign_receipt

ROOT = Path(__file__).resolve().parents[1]


def _probe():
    return {
        "engine": "LEAN",
        "probe_scope": "EquityFillModel.MarketOnOpenFill",
        "order_type": "MarketOnOpen",
        "status": "Filled",
        "fill_quantity": "5",
        "fill_price": "13",
        "fill_time": "2026-06-03T13:30:00+00:00",
        "source_event_id": "bar-3-open",
        "instrument_id": "AAA",
        "fill_message": "",
    }


def test_a2_controlled_campaign_is_reference_conformant_and_deterministic(tmp_path):
    spec = json.loads((ROOT / "fixtures/trader/a2-controlled-baseline-v1.json").read_text())
    pin = json.loads((ROOT / "contracts/execution/lean-a1-candidate-pin-v1.json").read_text())
    fixture, strategy_risk = prepare_controlled_fixture(spec)
    assert fixture["intents"][0]["side"] == "BUY"
    assert fixture["intents"][0]["created_at"] == spec["decision_time"]
    first = build_campaign_receipt(
        spec=spec,
        fixture=fixture,
        strategy_risk=strategy_risk,
        pin=pin,
        probe=_probe(),
        db_path=tmp_path / "first.db",
    )
    second = build_campaign_receipt(
        spec=spec,
        fixture=fixture,
        strategy_risk=strategy_risk,
        pin=pin,
        probe=_probe(),
        db_path=tmp_path / "second.db",
    )
    assert first == second
    assert first["differential_conformance"] == "PASS"
    assert first["authority"] == "NONE"
    assert first["nav"] == "1000"
    assert first["positions"] == [{"instrument_id": "AAA", "quantity": "5"}]
