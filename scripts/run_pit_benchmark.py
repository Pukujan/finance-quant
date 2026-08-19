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
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


def main() -> int:
    gold = MemoryGoldStore()
    with tempfile.TemporaryDirectory(prefix="fq-pit-bench-") as tmp:
        target = SQLiteBitemporalStore(Path(tmp) / "pit.db")
        for record in generate():
            gold.put(record)
            target.put(record)
        results = BakeoffHarness(target, gold, business_days(START, N_DAYS)).run_all()
        target.close()

    report = {
        "harness": "PIT Q1-Q8 V0",
        "candidate": "SQLiteBitemporalStore",
        "oracle": "MemoryGoldStore",
        "passed": all(r.passed_oracle for r in results),
        "queries": [
            {"query_id": r.query_id, "name": r.name, "row_count": r.row_count,
             "elapsed_ms": r.elapsed_ms, "passed_oracle": r.passed_oracle}
            for r in results
        ],
        "next_candidates": ["XTDB 2.x", "TimescaleDB", "ArcticDB (Apache-converted only)",
                            "Parquet+manifest"],
        "status": "V0 baseline measured; production bake-off pending adapter implementations",
    }
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
