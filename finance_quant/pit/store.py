"""PITStore interface + two implementations.

- MemoryGoldStore: pure-Python reference (the correctness oracle; deliberately slow).
- SQLiteBitemporalStore: durable bitemporal authority candidate.

Visibility rule (the whole game): a revision r of fact (ns, instrument, vt) is the
visible one at knowledge bound K iff r = max{ revision : kt <= K }. Corrections append
higher revisions; lower revisions are never deleted and remain reachable at older K.
"""
from __future__ import annotations

import hashlib
import sqlite3
import threading
from pathlib import Path
from typing import Iterable, Optional, Protocol

from .model import BitemporalRecord


class PITStore(Protocol):
    def put(self, record: BitemporalRecord) -> None: ...
    def as_of(self, namespace: str, instruments: Iterable[str],
              vt_start: str, vt_end: str, kt_bound: str) -> list[BitemporalRecord]: ...
    def revisions_between(self, kt_start: str, kt_end: str) -> list[BitemporalRecord]: ...
    def snapshot_pin(self) -> str: ...


def _visible(records: Iterable[BitemporalRecord], vt_start: str, vt_end: str,
             kt_bound: str) -> list[BitemporalRecord]:
    """Reference visibility: latest known revision per fact key, as of kt_bound."""
    best: dict[tuple, BitemporalRecord] = {}
    for rec in records:
        if not (vt_start <= rec.vt <= vt_end):
            continue
        if rec.kt > kt_bound:
            continue                      # not knowable yet: invisible (I1)
        cur = best.get(rec.key())
        if cur is None or rec.revision > cur.revision:
            best[rec.key()] = rec
    return sorted(best.values(), key=lambda r: r.key())


def _buried(records: Iterable[BitemporalRecord], kt_start: str, kt_end: str) -> list[BitemporalRecord]:
    out = [r for r in records if kt_start <= r.kt <= kt_end]
    return sorted(out, key=lambda r: (r.kt, *r.key(), r.revision))


def _pin(records: Iterable[BitemporalRecord]) -> str:
    """Immutable-history snapshot hash: every row, canonical order, supersessions included."""
    ordered = sorted(records, key=lambda r: (*r.key(), r.revision, r.kt))
    h = hashlib.blake2b(digest_size=32)
    for r in ordered:
        h.update(r.canonical())
    return h.hexdigest()


class MemoryGoldStore:
    def __init__(self) -> None:
        self._records: list[BitemporalRecord] = []

    def put(self, record: BitemporalRecord) -> None:
        self._records.append(record)

    def as_of(self, namespace, instruments, vt_start, vt_end, kt_bound):
        allowed = set(instruments)
        return _visible(
            (r for r in self._records
             if r.namespace == namespace and r.instrument_id in allowed),
            vt_start, vt_end, kt_bound,
        )

    def revisions_between(self, kt_start, kt_end):
        return _buried(self._records, kt_start, kt_end)

    def snapshot_pin(self) -> str:
        return _pin(self._records)


_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS records(
  namespace TEXT NOT NULL, instrument_id TEXT NOT NULL,
  vt TEXT NOT NULL, kt TEXT NOT NULL, revision INTEGER NOT NULL,
  payload TEXT NOT NULL, source TEXT NOT NULL,
  ingest_run_id TEXT NOT NULL, superseded_by INTEGER,
  PRIMARY KEY(namespace, instrument_id, vt, revision)
);
CREATE INDEX IF NOT EXISTS idx_asof ON records(namespace, instrument_id, vt, kt);
CREATE INDEX IF NOT EXISTS idx_kt ON records(kt);
"""


class SQLiteBitemporalStore:
    """Append-only bitemporal store. Deletes do not exist here by design (I7 for data)."""

    def __init__(self, path: str | Path):
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def put(self, record: BitemporalRecord) -> None:
        import json
        with self._lock:
            self._db.execute(
                "INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)",
                (record.namespace, record.instrument_id, record.vt, record.kt,
                 record.revision, json.dumps(record.payload, sort_keys=True),
                 record.source, record.ingest_run_id, record.superseded_by),
            )
        self._db.commit()

    def _rows(self, where: str, params: tuple) -> list[BitemporalRecord]:
        import json
        with self._lock:
            rows = self._db.execute(
                "SELECT namespace, instrument_id, vt, kt, revision, payload, source,"
                f" ingest_run_id, superseded_by FROM records WHERE {where}", params,
            ).fetchall()
        return [BitemporalRecord(*_decode(r)) for r in rows]

    def as_of(self, namespace, instruments, vt_start, vt_end, kt_bound):
        inst = list(instruments)
        if not inst:
            return []
        ph = ",".join("?" for _ in inst)
        # latest revision per (instrument, vt) among kt-visible rows
        sql = f"""
          SELECT r.namespace, r.instrument_id, r.vt, r.kt, r.revision,
                 r.payload, r.source, r.ingest_run_id, r.superseded_by
          FROM records r
          JOIN (
            SELECT instrument_id, vt, MAX(revision) AS maxrev
            FROM records
            WHERE namespace=? AND instrument_id IN ({ph})
              AND vt BETWEEN ? AND ? AND kt <= ?
            GROUP BY instrument_id, vt
          ) v ON v.instrument_id=r.instrument_id AND v.vt=r.vt AND v.maxrev=r.revision
          WHERE r.namespace=? AND r.kt <= ?
          ORDER BY r.instrument_id, r.vt
        """
        import json
        with self._lock:
            rows = self._db.execute(
                sql, (namespace, *inst, vt_start, vt_end, kt_bound, namespace, kt_bound)
            ).fetchall()
        return [BitemporalRecord(*_decode(r)) for r in rows]

    def revisions_between(self, kt_start, kt_end):
        return self._rows("kt BETWEEN ? AND ? ORDER BY kt, namespace, instrument_id, vt, revision",
                          (kt_start, kt_end))

    def snapshot_pin(self) -> str:
        return _pin(self._rows("1=1", ()))


def pit_depth_ok(store: PITStore, min_instruments: int = 4, min_bars: int = 10,
                 min_namespaces: set[str] | None = None) -> tuple[bool, str]:
    """Fast pre-flight check: does the store have enough bitemporal depth to run?

    This is the Phase B PIT-depth gate: a run must fail fast with a clear message
    if its input store is shallow, missing expected namespaces, or internally
    inconsistent. It is intentionally cheap (no full gold-oracle comparison).
    """
    required = min_namespaces or {"bar", "universe"}
    all_records = store._records if isinstance(store, MemoryGoldStore) else store._rows("1=1", ())

    namespaces = {r.namespace for r in all_records}
    missing = required - namespaces
    if missing:
        return False, f"missing required namespaces: {sorted(missing)}"

    bar_records = [r for r in all_records if r.namespace == "bar"]
    instruments = {r.instrument_id for r in bar_records}
    if len(instruments) < min_instruments:
        return False, f"only {len(instruments)} bar instruments, need >= {min_instruments}"

    days = {r.vt for r in bar_records}
    if len(days) < min_bars:
        return False, f"only {len(days)} bar days, need >= {min_bars}"

    # Knowledge-time must never precede valid-time for facts about market reality
    # (future-dated facts are forbidden). Corporate actions and universe changes are
    # announced before they are effective, so they legitimately have kt < vt; we skip
    # those namespaces in this structural check.
    bad_kt = [r for r in all_records
              if r.kt < r.vt and r.namespace not in {"corporate_action", "universe"}]
    if bad_kt:
        return False, f"{len(bad_kt)} records have kt < vt"

    return True, f"ok: {len(instruments)} instruments, {len(days)} days, {len(namespaces)} namespaces"


def _decode(row: tuple) -> tuple:
    """SQL column order -> BitemporalRecord constructor order."""
    import json
    (ns, inst, vt, kt, rev, payload, source, ingest, sup) = row
    return (ns, inst, vt, kt, json.loads(payload), source, rev, ingest) + (sup,)
