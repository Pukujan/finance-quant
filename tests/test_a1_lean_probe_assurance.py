from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.run_lean_a1_fill_probe import build_raw_lean_result, load_probe_result, verify_probe


FIXTURE_PATH = Path("fixtures/execution/a1-lean-fill-probe-v1.json")
PIN_PATH = Path("contracts/execution/lean-a1-candidate-pin-v1.json")


def _probe() -> dict[str, object]:
    return {
        "engine": "LEAN",
        "probe_scope": "EquityFillModel.MarketOnOpenFill",
        "status": "FILLED",
        "instrument_id": "AAA",
        "fill_quantity": "5",
        "fill_price": "11",
        "fill_time": "2026-06-02T13:30:00Z",
        "source_event_id": "bar-2",
    }


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "probe.out"
    path.write_text(text, encoding="utf-8")
    return path


def test_load_probe_result_accepts_explicit_trace_and_one_result(tmp_path: Path) -> None:
    text = "TRACE::2026-08-25 diagnostic\n" + json.dumps(_probe()) + "\n"
    assert load_probe_result(_write(tmp_path, text)) == _probe()


def test_load_probe_result_rejects_unprefixed_runtime_text(tmp_path: Path) -> None:
    text = "runtime diagnostic\n" + json.dumps(_probe()) + "\n"
    with pytest.raises(ValueError, match="unexpected non-JSON"):
        load_probe_result(_write(tmp_path, text))


@pytest.mark.parametrize(
    "text",
    [
        "TRACE::only diagnostics\n",
        json.dumps(_probe()) + "\n" + json.dumps(_probe()) + "\n",
        json.dumps({"engine": "OTHER", "probe_scope": "other"}) + "\n",
        json.dumps(_probe()) + "\n" + json.dumps({"other": "object"}) + "\n",
        json.dumps([_probe()]) + "\n",
    ],
)
def test_load_probe_result_requires_exactly_one_expected_object(tmp_path: Path, text: str) -> None:
    with pytest.raises(ValueError):
        load_probe_result(_write(tmp_path, text))


def test_valid_public_probe_still_conforms() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    evidence = verify_probe(_probe(), fixture, pin)
    assert evidence["semantic_conformance"] == "PASS"
    assert evidence["runtime_disposition"] == "PENDING"
    assert evidence["authority"] == "NONE"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("engine", "OTHER"),
        ("probe_scope", "CustomFillModel"),
        ("status", "CANCELED"),
        ("source_event_id", "bar-1"),
        ("fill_time", "2026-06-01T20:00:00Z"),
        ("instrument_id", "BBB"),
        ("fill_quantity", "4"),
        ("fill_price", "12"),
    ],
)
def test_probe_semantic_faults_fail_closed(field: str, value: str) -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    probe = copy.deepcopy(_probe())
    probe[field] = value
    with pytest.raises((AssertionError, KeyError, ValueError)):
        verify_probe(probe, fixture, pin)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("candidate", "OTHER"),
        ("runtime_disposition", "ADOPT"),
        ("credentials_required", True),
        ("cli_used", True),
    ],
)
def test_pin_authority_faults_fail_closed(field: str, value: object) -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    pin[field] = value
    with pytest.raises(ValueError):
        build_raw_lean_result(_probe(), fixture, pin)
