"""Tests for scripts/run_phase_b_mvfi.py.

Monkeypatches the PolygonAdapter transport to supply canned responses so
the script can be exercised end-to-end without a real API key or network.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.run_phase_b_mvfi import (
    count_expected_api_calls,
    main,
    run_mvfi,
    _compute_snapshot_pin,
    _records_to_bitemporal,
    _make_ingest_run_id,
)


# -- canned transport helpers ------------------------------------------------

def _make_bar_response(symbol: str, start: str, end: str) -> dict:
    """Return a minimal /v2/aggs response with two trading days."""
    return {
        "results": [
            {"t": 1704153600000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 1_000_000, "vw": 100.2, "n": 5000},
            {"t": 1704240000000, "o": 100.5, "h": 102.0, "l": 100.0, "c": 101.0, "v": 1_200_000, "vw": 100.8, "n": 5200},
        ],
        "next_url": None,
    }


def _make_dividend_response(symbol: str) -> dict:
    return {
        "results": [
            {
                "ex_dividend_date": "2024-01-05",
                "cash_amount": 0.25,
                "currency": "USD",
                "declaration_date": "2023-12-15",
                "record_date": "2024-01-08",
                "pay_date": "2024-01-20",
                "frequency": 4,
            }
        ],
        "next_url": None,
    }


def _make_split_response(symbol: str) -> dict:
    return {
        "results": [
            {
                "execution_date": "2024-01-10",
                "split_from": 1,
                "split_to": 2,
            }
        ],
        "next_url": None,
    }


def canned_transport(url: str, params: dict, api_key: str) -> dict:
    """Deterministic transport that returns canned data based on the URL path."""
    if "/v2/aggs/ticker/" in url:
        # Extract symbol from URL like /v2/aggs/ticker/AAPL/range/1/day/...
        parts = url.split("/v2/aggs/ticker/")[1].split("/")
        symbol = parts[0]
        return _make_bar_response(symbol, "", "")
    if "/v3/reference/dividends" in url:
        return _make_dividend_response("")
    if "/v3/reference/splits" in url:
        return _make_split_response("")
    return {"results": [], "next_url": None}


# -- tests -------------------------------------------------------------------

class TestCountExpectedApiCalls:
    def test_three_symbols(self):
        assert count_expected_api_calls(["AAPL", "MSFT", "GOOGL"]) == 9

    def test_empty(self):
        assert count_expected_api_calls([]) == 0

    def test_one_symbol(self):
        assert count_expected_api_calls(["AAPL"]) == 3


class TestComputeSnapshotPin:
    def test_deterministic(self):
        records = [
            {"a": 1, "b": 2},
            {"a": 3, "b": 4},
        ]
        assert _compute_snapshot_pin(records) == _compute_snapshot_pin(records)

    def test_order_independent(self):
        records_a = [{"x": 1}, {"y": 2}]
        records_b = [{"y": 2}, {"x": 1}]
        assert _compute_snapshot_pin(records_a) == _compute_snapshot_pin(records_b)

    def test_different_values(self):
        h1 = _compute_snapshot_pin([{"a": 1}])
        h2 = _compute_snapshot_pin([{"a": 2}])
        assert h1 != h2


class TestRecordsToBitemporal:
    def test_bar_conversion(self):
        raw = [{
            "namespace": "bar",
            "instrument_id": "AAPL",
            "vt": "2024-01-02T16:00:00+00:00",
            "kt": "2024-01-02T16:00:01+00:00",
            "payload": {"open": 100.0, "close": 100.5},
            "source": "polygon",
            "revision": 1,
            "superseded_by": None,
        }]
        result = _records_to_bitemporal(raw, "run-1")
        assert len(result) == 1
        rec = result[0]
        assert rec.vt == "2024-01-02"
        assert rec.kt == "2024-01-02"
        assert rec.ingest_run_id == "run-1"

    def test_corporate_action_conversion(self):
        raw = [{
            "namespace": "corporate_action",
            "instrument_id": "AAPL",
            "vt": "2024-01-05T00:00:00+00:00",
            "kt": "2024-01-03T00:00:00+00:00",
            "payload": {"kind": "dividend", "amount": 0.25},
            "source": "polygon",
            "revision": 1,
            "superseded_by": None,
        }]
        result = _records_to_bitemporal(raw, "run-1")
        assert len(result) == 1
        rec = result[0]
        assert rec.vt == "2024-01-05"
        assert rec.kt == "2024-01-03"
        assert rec.namespace == "corporate_action"


class TestMakeIngestRunId:
    def test_format(self):
        rid = _make_ingest_run_id(["AAPL", "MSFT"], "2024-01-01", "2024-01-31")
        assert rid == "mvfi-AAPL-MSFT-2024-01-01-2024-01-31"


class TestDryRun:
    def test_dry_run_returns_zero(self, tmp_path, monkeypatch):
        monkeypatch.setenv("POLYGON_API_KEY", "fake-key")
        rc = main([
            "--symbols", "AAPL", "MSFT",
            "--start", "2024-01-01",
            "--end", "2024-01-31",
            "--out-dir", str(tmp_path / "out"),
            "--dry-run",
        ])
        assert rc == 0


class TestMissingApiKey:
    def test_fails_without_key(self, monkeypatch):
        monkeypatch.delenv("POLYGON_API_KEY", raising=False)
        rc = main([
            "--symbols", "AAPL",
            "--start", "2024-01-01",
            "--end", "2024-01-31",
        ])
        assert rc == 1


class TestRunMvfiWithCannedTransport:
    """End-to-end script execution using a monkeypatched transport."""

    def test_full_ingest_writes_manifest_and_records(self, tmp_path):
        out_dir = tmp_path / "provisional"
        with patch("scripts.run_phase_b_mvfi.PolygonAdapter") as MockAdapter:
            instance = MockAdapter.return_value
            instance.source = "polygon"
            instance.fetch_bars.return_value = [
                {
                    "namespace": "bar",
                    "instrument_id": "AAPL",
                    "vt": "2024-01-02T16:00:00+00:00",
                    "kt": "2024-01-02T16:00:01+00:00",
                    "payload": {"open": 100.0, "close": 100.5},
                    "source": "polygon",
                    "revision": 1,
                    "superseded_by": None,
                }
            ]
            instance.fetch_corporate_actions.return_value = []

            rc = run_mvfi(
                symbols=["AAPL"],
                start="2024-01-01",
                end="2024-01-31",
                out_dir=out_dir,
                api_key="fake",
                dry_run=False,
            )
            assert rc == 0

            manifest_path = out_dir / "manifest.json"
            assert manifest_path.exists()
            manifest = json.loads(manifest_path.read_text())
            assert manifest["manifest_id"] == "provisional-fixture-v0"
            assert manifest["record_count"] >= 1
            assert "snapshot_pin" in manifest
            assert manifest["source_metadata"]["vendor"] == "polygon"

            records_path = out_dir / "records.jsonl"
            assert records_path.exists()
            lines = records_path.read_text().strip().splitlines()
            assert len(lines) >= 1

            db_path = out_dir / "pit.db"
            assert db_path.exists()

    def test_empty_results_proceeds(self, tmp_path):
        out_dir = tmp_path / "empty"
        with patch("scripts.run_phase_b_mvfi.PolygonAdapter") as MockAdapter:
            instance = MockAdapter.return_value
            instance.source = "polygon"
            instance.fetch_bars.return_value = []
            instance.fetch_corporate_actions.return_value = []

            rc = run_mvfi(
                symbols=["NOPRICE"],
                start="2024-01-01",
                end="2024-01-31",
                out_dir=out_dir,
                api_key="fake",
                dry_run=False,
            )
            assert rc == 0
            manifest = json.loads((out_dir / "manifest.json").read_text())
            assert manifest["record_count"] == 0


class TestMainIntegration:
    """Test the CLI entry point with a patched adapter."""

    def test_main_with_canned_transport(self, tmp_path, monkeypatch):
        monkeypatch.setenv("POLYGON_API_KEY", "test-key")
        out_dir = tmp_path / "fixture"

        def fake_fetch_bars(self, symbol, start, end):
            return [{
                "namespace": "bar",
                "instrument_id": symbol,
                "vt": "2024-01-02T16:00:00+00:00",
                "kt": "2024-01-02T16:00:01+00:00",
                "payload": {"open": 100.0, "close": 100.5, "high": 101.0, "low": 99.0, "volume": 1000, "vwap": 100.2, "trades": 50},
                "source": "polygon",
                "revision": 1,
                "superseded_by": None,
            }]

        def fake_fetch_ca(self, symbol, start, end):
            return []

        from scripts.run_phase_b_mvfi import PolygonAdapter as RealAdapter
        with patch.object(RealAdapter, "fetch_bars", fake_fetch_bars), \
             patch.object(RealAdapter, "fetch_corporate_actions", fake_fetch_ca):
            rc = main([
                "--symbols", "TEST1", "TEST2",
                "--start", "2024-01-01",
                "--end", "2024-01-31",
                "--out-dir", str(out_dir),
            ])
            assert rc == 0
            assert (out_dir / "manifest.json").exists()
            assert (out_dir / "records.jsonl").exists()
            assert (out_dir / "pit.db").exists()
