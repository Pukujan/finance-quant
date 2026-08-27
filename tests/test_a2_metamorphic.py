from __future__ import annotations

import json
from copy import deepcopy
from itertools import permutations
from pathlib import Path

from scripts.prepare_a2_controlled_fixture import prepare_controlled_fixture

ROOT = Path(__file__).resolve().parents[1]


def _spec():
    return json.loads((ROOT / "fixtures/trader/a2-controlled-baseline-v1.json").read_text())


def test_metamorphic_event_permutation_preserves_strategy_risk_and_execution_fixture():
    spec = _spec()
    expected_fixture, expected_evidence = prepare_controlled_fixture(spec)
    for ordering in permutations(spec["events"]):
        transformed = deepcopy(spec)
        transformed["events"] = list(ordering)
        fixture, evidence = prepare_controlled_fixture(transformed)
        assert fixture == expected_fixture
        assert evidence == expected_evidence


def test_metamorphic_exact_duplicate_and_unrelated_event_do_not_change_decision_lineage():
    spec = _spec()
    expected_fixture, expected_evidence = prepare_controlled_fixture(spec)

    duplicate = deepcopy(spec)
    duplicate["events"].append(deepcopy(spec["events"][0]))
    fixture, evidence = prepare_controlled_fixture(duplicate)
    assert fixture == expected_fixture
    assert evidence == expected_evidence

    unrelated = deepcopy(spec)
    unrelated["events"].append(
        {
            "event_id": "unrelated",
            "instrument_id": "BBB",
            "event_time": "2026-06-02T19:00:00Z",
            "known_at": "2026-06-02T19:00:00Z",
            "sequence": 99,
            "payload": {"open": "1", "high": "100", "low": "1", "close": "100", "liquidity": "100"},
        }
    )
    fixture, evidence = prepare_controlled_fixture(unrelated)
    assert evidence == expected_evidence
    assert fixture["intents"] == expected_fixture["intents"]
