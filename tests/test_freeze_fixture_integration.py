"""Integration test for freeze_fixture wired to the real SQLite PITStore."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure root is on sys.path (same logic as conftest.py).
_here = Path(__file__).resolve()
ROOT = _here.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
import tempfile
from scripts.freeze_fixture import (
    canonical_json,
    compute_manifest_hash,
    export_records,
    load_store,
    verify_manifest,
    write_manifest,
)
from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_rows(tmp_path: Path) -> Path:
    """Create a small temp SQLite PITStore and return its path."""
    db_path = tmp_path / "test_pit.db"
    store = SQLiteBitemporalStore(db_path)

    recs = [
        BitemporalRecord(
            namespace="bar",
            instrument_id="XAA",
            vt="2025-03-01",
            kt="2025-03-01",
            payload={"open": 10.0, "high": 11.0, "low": 9.5, "close": 10.5, "volume": 500},
            source="test",
            revision=0,
        ),
        BitemporalRecord(
            namespace="bar",
            instrument_id="xBB",
            vt="2025-03-01",
            kt="2025-03-01",
            payload={"open": 20.0, "high": 22.0, "low": 19.0, "close": 21.0, "volume": 700},
            source="test",
            revision=0,
        ),
        # Second day for XAA to test visibility rule
        BitemporalRecord(
            namespace="bar",
            instrument_id="XAA",
            vt="2025-03-02",
            kt="2025-03-02",
            payload={"open": 12.0, "high": 13.0, "low": 11.5, "close": 12.5, "volume": 600},
            source="test",
            revision=0,
        ),
    ]

    for r in recs:
        store.put(r)
    return db_path


def _make_gold_stored() -> MemoryGoldStore:
    store = MemoryGoldStore()
    recs = [
        BitemporalRecord(
            namespace="bar",
            instrument_id="FAA",
            vt="2025-01-01",
            kt="2025-01-01",
            payload={"foo": 42},
            source="test",
            revision=0,
        ),
    ]
    for r in recs:
        store.put(r)
    return store


# ---------------------------------------------------------------------------
# Tests: load_store with real file path
# ---------------------------------------------------------------------------

class TestLoadStoreRealFile:
    def test_load_returns_sqlite_store(self, tmp_path):
        db_path = _make_test_rows(tmp_path)
        store = load_store(db_path)
        assert isinstance(store, SQLiteBitemporalStore), "load_store(path) must return SQLiteBitemporalStore"

    def test_dump_records_from_file(self, tmp_path):
        db_path = _make_test_rows(tmp_path)
        store = load_store(db_path)
        records = store.dump_records()
        assert len(records) == 3
        assert records[0]["instrument_id"] == "XAA"
        assert records[0]["namespace"] == "bar"
        assert records[0]["vt"] == "2025-03-01"

    def test_roundtrip_via_export_and_manifest(self, tmp_path):
        db_path = _make_test_rows(tmp_path)
        store = load_store(db_path)
        records = store.dump_records()
        fixture_dir = tmp_path / "fixtures" / "phase-b"

        export_records(records, fixture_dir)
        h = compute_manifest_hash(records)
        write_manifest(fixture_dir, h, len(records))

        assert (fixture_dir / "records.jsonl").exists()
        assert (fixture_dir / "manifest.json").exists()

        # Read jsonl back
        lines = (fixture_dir / "records.jsonl").read_text(encoding="utf-8").strip().splitlines()
        back = [json.loads(l) for l in lines]
        assert len(back) == len(records)
        for orig, decoded in zip(records, back):
            assert orig["instrument_id"] == decoded["instrument_id"]
            assert orig["namespace"] == decoded["namespace"]
            assert orig["payload"] == decoded["payload"]
            assert orig["source"] == decoded["source"]
            assert orig["revision"] == decoded["revision"]

    def test_verify_manifest_passes(self, tmp_path):
        db_path = _make_test_rows(tmp_path)
        store = load_store(db_path)
        records = store.dump_records()
        fixture_dir = tmp_path / "fixtures" / "phase-b"

        export_records(records, fixture_dir)
        h = compute_manifest_hash(records)
        write_manifest(fixture_dir, h, len(records))

        verified = verify_manifest(fixture_dir, records)
        assert verified is True


class TestLoadStoreInMemoryStub:
    """When path is None or missing, load_store falls back to in-memory dummy."""

    def test_none_path_returns_dumpster(self, tmp_path):
        os_tmpdir = tempfile.gettempdir()
        with tempfile.TemporaryDirectory(dir=os_tmpdir) as td:
            store = load_store(None)
            records = store.dump_records()
            assert len(records) == 2
            assert records[0]["instrument_id"] == "AAA"
            assert records[1]["instrument_id"] == "BBB"

    def test_nonexistent_path_falls_back(self, tmp_path):
        fake_path = tmp_path / "nonexistent.db"
        assert not fake_path.exists()
        store = load_store(fake_path)
        records = store.dump_records()
        assert len(records) == 2


class TestDumpRecordsFromMemory:
    """MemoryGoldStore.dump_records should return dicts for every record."""

    def test_goldstore_dump(self):
        gs = _make_gold_stored()
        records = gs.dump_records()
        assert len(records) == 1
        assert records[0]["instrument_id"] == "FAA"
        assert records[0]["payload"]["foo"] == 42


class TestSnapshotPinFix:
    """SQLiteBitemporalStore.snapshot_pin must call _rows, not self._records."""

    def test_snapshot_pin_on_empty_sqlite(self, tmp_path):
        path = tmp_path / "empty.db"
        store = SQLiteBitemporalStore(path)
        pin = store.snapshot_pin()
        assert len(pin) == 64  # blake2b hex digest
        store.close()
