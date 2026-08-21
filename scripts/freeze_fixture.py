"""Canonical fixture freeze for Phase B.

Promotes an ingested PIT dataset to a canonical fixture under
``data/fixtures/phase-b/`` and pins its manifest hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


FIXTURE_DIR = Path("data/fixtures/phase-b")
MANIFEST_NAME = "manifest.json"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def compute_manifest_hash(records: Iterable[dict]) -> str:
    """Stable SHA-256 over canonically-serialized, length-prefixed records."""
    h = hashlib.sha256()
    for rec in sorted(records, key=lambda r: canonical_json(r)):
        blob = canonical_json(rec)
        h.update(len(blob).to_bytes(8, "big"))
        h.update(blob.encode("utf-8"))
    return h.hexdigest()


def load_store(path: Path) -> "StubPITStore":
    """Load a PIT store.  Defaults to an in-memory stub for CI/demos."""
    if not path or not path.exists():
        return StubPITStore()
    # Production path would import finance_quant.pit and open a real store.
    raise NotImplementedError("real PITStore loading is a TODO; use default stub")


class StubPITStore:
    """In-memory stub producing a tiny deterministic fixture."""

    def as_of(self, vt: str | None = None, kt: str | None = None) -> list[dict]:
        return [
            {
                "instrument_id": "AAA",
                "namespace": "bar",
                "vt": "2024-01-02T16:00:00-05:00",
                "kt": "2024-01-02T16:00:01.123000-05:00",
                "payload": {"open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 1000},
                "source": "polygon",
                "revision": 1,
                "superseded_by": None,
            },
            {
                "instrument_id": "BBB",
                "namespace": "bar",
                "vt": "2024-01-02T16:00:00-05:00",
                "kt": "2024-01-02T16:00:01.123000-05:00",
                "payload": {"open": 2.0, "high": 2.2, "low": 1.9, "close": 2.1, "volume": 2000},
                "source": "polygon",
                "revision": 1,
                "superseded_by": None,
            },
        ]

    def dump_records(self) -> list[dict]:
        return self.as_of()


def export_records(records: list[dict], fixture_dir: Path) -> Path:
    """Write records as JSONL under fixture_dir."""
    fixture_dir.mkdir(parents=True, exist_ok=True)
    data_path = fixture_dir / "records.jsonl"
    with data_path.open("w", encoding="utf-8") as stream:
        for rec in records:
            stream.write(canonical_json(rec) + "\n")
    return data_path


def write_manifest(fixture_dir: Path, manifest_hash: str, record_count: int) -> Path:
    manifest = {
        "manifest_id": "phase-b-fixture-v0",
        "snapshot_pin": manifest_hash,
        "record_count": record_count,
        "fixture_path": str(fixture_dir / "records.jsonl"),
    }
    path = fixture_dir / MANIFEST_NAME
    path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    return path


def verify_manifest(fixture_dir: Path, records: list[dict]) -> bool:
    manifest_path = fixture_dir / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = compute_manifest_hash(records)
    if manifest.get("snapshot_pin") != expected:
        raise ValueError(f"snapshot_pin mismatch: {manifest.get('snapshot_pin')} != {expected}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze or verify a Phase B fixture")
    parser.add_argument("--store-path", type=Path, default=None)
    parser.add_argument("--fixture-dir", type=Path, default=FIXTURE_DIR)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    store = load_store(args.store_path)
    records = store.dump_records()

    if args.verify:
        verify_manifest(args.fixture_dir, records)
        print(f"verified {args.fixture_dir}")
        return 0

    export_records(records, args.fixture_dir)
    manifest_hash = compute_manifest_hash(records)
    write_manifest(args.fixture_dir, manifest_hash, len(records))
    print(f"froze {len(records)} records to {args.fixture_dir} with hash {manifest_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
