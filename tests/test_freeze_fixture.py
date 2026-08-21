from pathlib import Path

import pytest

from scripts.freeze_fixture import (
    compute_manifest_hash,
    export_records,
    load_store,
    verify_manifest,
    write_manifest,
)


@pytest.fixture
def sample_records():
    return [
        {"instrument_id": "AAA", "namespace": "bar", "vt": "2024-01-02", "kt": "2024-01-02T00:00:01Z"},
        {"instrument_id": "BBB", "namespace": "bar", "vt": "2024-01-02", "kt": "2024-01-02T00:00:01Z"},
    ]


def test_load_store_stub():
    store = load_store(None)
    records = store.dump_records()
    assert len(records) == 2
    assert records[0]["namespace"] == "bar"


def test_compute_manifest_hash_deterministic(sample_records):
    h1 = compute_manifest_hash(sample_records)
    h2 = compute_manifest_hash(sample_records)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_manifest_hash_order_independent(sample_records):
    reversed_records = list(reversed(sample_records))
    assert compute_manifest_hash(sample_records) == compute_manifest_hash(reversed_records)


def test_export_and_manifest_roundtrip(tmp_path, sample_records):
    fixture_dir = tmp_path / "phase-b"
    export_records(sample_records, fixture_dir)
    manifest_hash = compute_manifest_hash(sample_records)
    write_manifest(fixture_dir, manifest_hash, len(sample_records))
    assert (fixture_dir / "records.jsonl").exists()
    assert (fixture_dir / "manifest.json").exists()
    verify_manifest(fixture_dir, sample_records)


def test_verify_manifest_bad_hash(tmp_path, sample_records):
    fixture_dir = tmp_path / "phase-b"
    export_records(sample_records, fixture_dir)
    write_manifest(fixture_dir, "0" * 64, len(sample_records))
    with pytest.raises(ValueError, match="snapshot_pin mismatch"):
        verify_manifest(fixture_dir, sample_records)
