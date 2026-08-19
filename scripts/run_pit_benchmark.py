"""Candidate storage benchmark: SQLite vs in-memory gold (spike #2 V0).

This is a measured baseline, not a winner declaration. XTDB, TimescaleDB, ArcticDB
(license-constrained), and Parquet+manifest remain the required production candidates.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.pit.bakeoff import BakeoffHarness
from finance_quant.pit.fixtures import N_DAYS, START, business_days, generate
from finance_quant.pit.manifest_store import ManifestJsonlStore
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


def _load(store, records):
    for record in records:
        store.put(record)
    return store


def main() -> int:
    records = generate()
    gold = _load(MemoryGoldStore(), records)
    days = business_days(START, N_DAYS)
    tmp = Path(tempfile.mkdtemp(prefix="fq-pit-bench-"))
    sqlite = _load(SQLiteBitemporalStore(tmp / "pit.db"), records)
    jsonl = _load(ManifestJsonlStore(tmp / "pit.jsonl"), records)
    sqlite_results = BakeoffHarness(sqlite, gold, days).run_all()
    jsonl_results = BakeoffHarness(jsonl, gold, days).run_all()
    pins_match = sqlite.snapshot_pin() == jsonl.snapshot_pin() == gold.snapshot_pin()
    sqlite.close()

    report = {
        "harness": "PIT Q1-Q8 V0",
        "oracle": "MemoryGoldStore",
        "candidates": {
            "SQLiteBitemporalStore": {
                "passed": all(r.passed_oracle for r in sqlite_results),
                "queries": [
                    {"query_id": r.query_id, "elapsed_ms": r.elapsed_ms, "passed_oracle": r.passed_oracle}
                    for r in sqlite_results
                ],
            },
            "ManifestJsonlStore": {
                "passed": all(r.passed_oracle for r in jsonl_results),
                "queries": [
                    {"query_id": r.query_id, "elapsed_ms": r.elapsed_ms, "passed_oracle": r.passed_oracle}
                    for r in jsonl_results
                ],
            },
        },
        "pins_match": pins_match,
        "next_candidates": ["XTDB 2.x", "TimescaleDB", "ArcticDB (Apache-converted only)"],
        "status": "V0: SQLite and JSONL+manifest match gold; remaining candidates need adapters",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["candidates"]["SQLiteBitemporalStore"]["passed"] and report["candidates"]["ManifestJsonlStore"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
