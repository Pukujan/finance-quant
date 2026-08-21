"""Minimum Viable First Ingest (MVFI) script for Phase B.

Fetches daily adjusted bars and corporate actions for a small symbol set
via the Polygon adapter, writes them into a fresh SQLite PIT store, and
emits a provisional manifest named ``provisional-fixture-v0``.

Usage examples
--------------
Normal run::

    POLYGON_API_KEY=xxx python scripts/run_phase_b_mvfi.py \
        --symbols AAPL MSFT GOOGL AMZN TSLA \
        --start 2024-01-01 --end 2024-01-31 \
        --out-dir data/provisional-fixture-v0

Dry-run (counts expected API calls only)::

    POLYGON_API_KEY=xxx python scripts/run_phase_b_mvfi.py \
        --symbols AAPL MSFT GOOGL AMZN TSLA \
        --start 2024-01-01 --end 2024-01-31 \
        --out-dir data/provisional-fixture-v0 \
        --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from finance_quant.ingest.polygon import PolygonAdapter
from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import SQLiteBitemporalStore


MANIFEST_NAME = "manifest.json"
STORE_NAME = "pit.db"


def _iso_date(value: str) -> str:
    """Truncate an ISO timestamp to day granularity YYYY-MM-DD."""
    if len(value) >= 10:
        return value[:10]
    return value


def _make_ingest_run_id(symbols: list[str], start: str, end: str) -> str:
    return f"mvfi-{'-'.join(symbols)}-{start}-{end}"


def _records_to_bitemporal(raw: list[dict], ingest_run_id: str) -> list[BitemporalRecord]:
    """Convert adapter dict records into BitemporalRecord instances.

    Normalises vt/kt to YYYY-MM-DD to satisfy the PIT contract.
    """
    out: list[BitemporalRecord] = []
    for r in raw:
        out.append(BitemporalRecord(
            namespace=r["namespace"],
            instrument_id=r["instrument_id"],
            vt=_iso_date(r["vt"]),
            kt=_iso_date(r["kt"]),
            payload=r["payload"],
            source=r["source"],
            revision=r["revision"],
            ingest_run_id=ingest_run_id,
            superseded_by=r.get("superseded_by"),
        ))
    return out


def _dump_records(store: SQLiteBitemporalStore) -> list[dict]:
    return store.dump_records()


def _write_manifest(out_dir: Path, records: list[dict], symbols: list[str],
                    start: str, end: str, source: str) -> Path:
    """Emit a provisional manifest with snapshot_pin and metadata."""
    out_dir.mkdir(parents=True, exist_ok=True)

    h = _compute_snapshot_pin(records)

    manifest: dict[str, Any] = {
        "manifest_id": "provisional-fixture-v0",
        "snapshot_pin": h,
        "record_count": len(records),
        "date_range": {"start": start, "end": end},
        "symbols": sorted(symbols),
        "source_metadata": {
            "vendor": source,
            "ingest_type": "mvfi",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "store_path": str(out_dir / STORE_NAME),
        "data_path": str(out_dir / "records.jsonl"),
    }

    manifest_path = out_dir / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _compute_snapshot_pin(records: list[dict]) -> str:
    """SHA-256 pin over canonically serialised records (length-prefixed)."""
    import hashlib
    h = hashlib.sha256()
    for rec in sorted(records, key=lambda r: json.dumps(r, sort_keys=True, default=str)):
        blob = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
        h.update(len(blob).to_bytes(8, "big"))
        h.update(blob.encode("utf-8"))
    return h.hexdigest()


def _write_records_jsonl(out_dir: Path, records: list[dict]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    data_path = out_dir / "records.jsonl"
    with data_path.open("w", encoding="utf-8") as f:
        for rec in sorted(records, key=lambda r: json.dumps(r, sort_keys=True, default=str)):
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str) + "\n")
    return data_path


def count_expected_api_calls(symbols: list[str]) -> int:
    """Count how many HTTP calls the ingest would make (1 bars + 2 corp-actions per symbol)."""
    return len(symbols) * 3  # bars + dividends + splits per symbol


def run_mvfi(
    symbols: list[str],
    start: str,
    end: str,
    out_dir: Path,
    api_key: str,
    dry_run: bool = False,
) -> int:
    """Execute the MVFI ingest or dry-run.

    Returns 0 on success, non-zero on failure.
    """
    ingest_run_id = _make_ingest_run_id(symbols, start, end)

    if dry_run:
        calls = count_expected_api_calls(symbols)
        print(f"[dry-run] Expected API calls: {calls}")
        print(f"[dry-run] Symbols: {symbols}")
        print(f"[dry-run] Date range: {start} to {end}")
        print(f"[dry-run] Output dir: {out_dir}")
        return 0

    adapter = PolygonAdapter(api_key=api_key)

    out_dir.mkdir(parents=True, exist_ok=True)
    store = SQLiteBitemporalStore(out_dir / STORE_NAME)

    all_raw: list[dict] = []
    for sym in symbols:
        print(f"Fetching bars for {sym} ({start} to {end})...")
        bars = adapter.fetch_bars(sym, start, end)
        all_raw.extend(bars)
        print(f"  -> {len(bars)} bar records")

        print(f"Fetching corporate actions for {sym}...")
        ca = adapter.fetch_corporate_actions(sym, start, end)
        all_raw.extend(ca)
        print(f"  -> {len(ca)} corporate action records")

    if not all_raw:
        print("WARNING: no records fetched; store will be empty")

    bt_records = _records_to_bitemporal(all_raw, ingest_run_id)
    for rec in bt_records:
        store.put(rec)

    records = _dump_records(store)

    manifest_path = _write_manifest(out_dir, records, symbols, start, end, adapter.source)
    _write_records_jsonl(out_dir, records)

    print(f"Wrote {len(records)} records to {out_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"Snapshot pin: {manifest_path.read_text(encoding='utf-8').strip()}")

    store.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase B Minimum Viable First Ingest (MVFI)")
    parser.add_argument("--symbols", nargs="+", default=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
                        help="Symbols to fetch (default: 5 tech symbols)")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--out-dir", type=Path, default=Path("data/provisional-fixture-v0"),
                        help="Output directory (default: data/provisional-fixture-v0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Only count expected API calls; do not fetch or write")

    args = parser.parse_args(argv)

    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        print("ERROR: POLYGON_API_KEY environment variable is required", file=sys.stderr)
        return 1

    return run_mvfi(
        symbols=args.symbols,
        start=args.start,
        end=args.end,
        out_dir=args.out_dir,
        api_key=api_key,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
