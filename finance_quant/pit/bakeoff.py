"""Bake-off query harness (spike #2 sec. 3).

Executes the Q1-Q8 query suite over any PITStore loaded with the canonical fixture,
measuring correctness vs the MemoryGoldStore oracle and tracking timing.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Tuple

from .fixtures import DELIST_EFFECTIVE, DELIST_KNOWN, START, SYMBOLS, business_days
from .model import BitemporalRecord
from .store import MemoryGoldStore, PITStore


@dataclass(frozen=True)
class QueryResult:
    query_id: str
    name: str
    row_count: int
    elapsed_ms: float
    fingerprint: str
    passed_oracle: bool


class BakeoffHarness:
    """Runs the 8 canonical queries against a target PITStore, checking oracle parity."""

    def __init__(self, target: PITStore, oracle: MemoryGoldStore, days: list[str]):
        self.target = target
        self.oracle = oracle
        self.days = days
        self.mid_day = days[len(days) // 2]
        self.last_day = days[-1]

    def _timed(self, qid: str, name: str, fn_target, fn_oracle) -> QueryResult:
        t0 = time.perf_counter()
        res_target = fn_target()
        t1 = time.perf_counter()
        res_oracle = fn_oracle()

        target_fps = [r.canonical() for r in res_target]
        oracle_fps = [r.canonical() for r in res_oracle]
        passed = target_fps == oracle_fps

        return QueryResult(
            query_id=qid,
            name=name,
            row_count=len(res_target),
            elapsed_ms=(t1 - t0) * 1000.0,
            fingerprint=hashlib.sha256(b"\n".join(target_fps)).hexdigest(),
            passed_oracle=passed,
        )

    def run_all(self) -> list[QueryResult]:
        results = []

        # Q1: Cross-sectional snapshot AS OF (mid_day, mid_day)
        results.append(self._timed(
            "Q1", "Full-universe cross section AS OF (t, t)",
            lambda: self.target.as_of("bar", SYMBOLS, self.mid_day, self.mid_day, self.mid_day),
            lambda: self.oracle.as_of("bar", SYMBOLS, self.mid_day, self.mid_day, self.mid_day),
        ))

        # Q2: Single symbol deep history AS OF mid_day
        results.append(self._timed(
            "Q2", "Single-symbol deep history AS OF kt",
            lambda: self.target.as_of("bar", ["AAA"], self.days[0], self.last_day, self.mid_day),
            lambda: self.oracle.as_of("bar", ["AAA"], self.days[0], self.last_day, self.mid_day),
        ))

        # Q3: Audit revisions between knowledge times (I7 visibility)
        results.append(self._timed(
            "Q3", "Revisions between knowledge-times k1, k2",
            lambda: self.target.revisions_between(self.days[0], self.last_day),
            lambda: self.oracle.revisions_between(self.days[0], self.last_day),
        ))

        # Q4: Restatement drill - Fundamentals knowable BEFORE restatement storm
        # Before restatement storm (early knowledge time: 2024-02-15)
        early_kt = "2024-02-15"
        results.append(self._timed(
            "Q4a", "Fundamentals AS OF early kt (pre-restatement)",
            lambda: self.target.as_of("fundamental", SYMBOLS, "2023-01-01", "2023-12-31", early_kt),
            lambda: self.oracle.as_of("fundamental", SYMBOLS, "2023-01-01", "2023-12-31", early_kt),
        ))

        # Q4b: Restatement drill - Fundamentals knowable AFTER restatement storm (2024-06-01)
        late_kt = "2024-06-01"
        results.append(self._timed(
            "Q4b", "Fundamentals AS OF late kt (post-restatement)",
            lambda: self.target.as_of("fundamental", SYMBOLS, "2023-01-01", "2023-12-31", late_kt),
            lambda: self.oracle.as_of("fundamental", SYMBOLS, "2023-01-01", "2023-12-31", late_kt),
        ))

        # Q5: Universe membership AS OF pre-delisting vs post-delisting
        results.append(self._timed(
            "Q5", "Universe membership AS OF pre-delisting announcement",
            lambda: self.target.as_of("universe", ["ZZZ"], "2024-01-01", "2024-03-01", "2024-02-01"),
            lambda: self.oracle.as_of("universe", ["ZZZ"], "2024-01-01", "2024-03-01", "2024-02-01"),
        ))

        # Q6: Corporate action point-in-time discovery (split known before effective)
        results.append(self._timed(
            "Q6", "Corporate actions known as of announcement date",
            lambda: self.target.as_of("corporate_action", ["CCC"], "2024-01-01", "2024-03-01", "2024-02-05"),
            lambda: self.oracle.as_of("corporate_action", ["CCC"], "2024-01-01", "2024-03-01", "2024-02-05"),
        ))

        # Q7: Bulk export for training (rolling window extraction across all symbols)
        results.append(self._timed(
            "Q7", "Bulk training window extract AS OF cutoff",
            lambda: self.target.as_of("bar", SYMBOLS, self.days[0], self.mid_day, self.mid_day),
            lambda: self.oracle.as_of("bar", SYMBOLS, self.days[0], self.mid_day, self.mid_day),
        ))

        # Q8: Snapshot pin identity (manifest hash over all history)
        pin_target = self.target.snapshot_pin()
        pin_oracle = self.oracle.snapshot_pin()
        results.append(QueryResult(
            query_id="Q8",
            name="Immutable dataset snapshot pin identity",
            row_count=1,
            elapsed_ms=0.0,
            fingerprint=pin_target,
            passed_oracle=(pin_target == pin_oracle),
        ))

        return results
