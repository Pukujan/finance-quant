import json

import pytest

from scripts.run_lean_a1_fill_probe import load_probe_result


PROBE = {
    "engine": "LEAN",
    "probe_scope": "EquityFillModel.MarketOnOpenFill",
    "order_type": "MarketOnOpen",
    "status": "Filled",
    "fill_quantity": "5",
    "fill_price": "11",
    "fill_time": "2026-06-02T13:30:00.0000000Z",
    "source_event_id": "bar-2",
    "instrument_id": "AAA",
    "fill_message": "",
}


def test_load_probe_result_accepts_single_result_after_runtime_trace(tmp_path):
    path = tmp_path / "probe.txt"
    path.write_text(
        "20260825 TRACE:: Composer(): Loading Assemblies\n"
        + json.dumps(PROBE)
        + "\n",
        encoding="utf-8",
    )

    assert load_probe_result(path) == PROBE


def test_load_probe_result_rejects_missing_result(tmp_path):
    path = tmp_path / "probe.txt"
    path.write_text("20260825 TRACE:: Composer(): Loading Assemblies\n", encoding="utf-8")

    with pytest.raises(ValueError, match="found 0"):
        load_probe_result(path)


def test_load_probe_result_rejects_multiple_matching_results(tmp_path):
    path = tmp_path / "probe.txt"
    encoded = json.dumps(PROBE)
    path.write_text(encoded + "\n" + encoded + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="found 2"):
        load_probe_result(path)
