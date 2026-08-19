"""Run the Phase-A PIT Q1-Q8 harness against its V0 candidates.

This is deliberately a harness result, not an architecture winner declaration:
the #2 decision constrained the production bake-off to XTDB, TimescaleDB,
ArcticDB (license-constrained), and Parquet+manifest. V0 establishes the
correctness corpus with MemoryGoldStore and SQLiteBitemporalStore first.

Run: python scripts/run_pit_bakeoff.py
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
    with tempfile.TemporaryDirectory(prefix="fq-pit-bakeoff-") as tmp:
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
        "queries": [r.__dict__ for r in results],
        "next_candidates": ["XTDB 2.x", "TimescaleDB", "ArcticDB (Apache-converted only)",
                            "Parquet+manifest"],
    }
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
