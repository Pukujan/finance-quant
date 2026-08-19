"""Optional TimescaleDB PIT adapter. V0 tests skip unless FQ_TIMESCALE_DSN is set.

This is a candidate implementation for spike #2, not the production authority.
Schema: bitemporal rows with (namespace, instrument_id, vt, revision) PK.
"""
from __future__ import annotations

import json
import os
from typing import Iterable

from .model import BitemporalRecord
from .store import _pin, _visible, _buried


def timescale_dsn() -> str | None:
    return os.environ.get("FQ_TIMESCALE_DSN")


class TimescalePITStore:
    def __init__(self, dsn: str):
        import psycopg
        self._conn = psycopg.connect(dsn, autocommit=True)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pit_records (
              namespace TEXT NOT NULL,
              instrument_id TEXT NOT NULL,
              vt TEXT NOT NULL,
              kt TEXT NOT NULL,
              revision INTEGER NOT NULL,
              payload JSONB NOT NULL,
              source TEXT NOT NULL,
              ingest_run_id TEXT NOT NULL,
              superseded_by INTEGER,
              PRIMARY KEY (namespace, instrument_id, vt, revision)
            )
            """
        )

    def close(self) -> None:
        self._conn.close()

    def put(self, record: BitemporalRecord) -> None:
        self._conn.execute(
            """INSERT INTO pit_records
               (namespace, instrument_id, vt, kt, revision, payload, source, ingest_run_id, superseded_by)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)""",
            (record.namespace, record.instrument_id, record.vt, record.kt, record.revision,
             json.dumps(record.payload), record.source, record.ingest_run_id, record.superseded_by),
        )

    def _all(self) -> list[BitemporalRecord]:
        rows = self._conn.execute(
            "SELECT namespace, instrument_id, vt, kt, revision, payload, source, ingest_run_id, superseded_by FROM pit_records"
        ).fetchall()
        return [BitemporalRecord(r[0], r[1], r[2], r[3], r[5] if isinstance(r[5], dict) else json.loads(r[5]),
                                 r[6], r[4], r[7], r[8]) for r in rows]

    def as_of(self, namespace, instruments, vt_start, vt_end, kt_bound):
        allowed = set(instruments)
        return _visible(
            (r for r in self._all() if r.namespace == namespace and r.instrument_id in allowed),
            vt_start, vt_end, kt_bound,
        )

    def revisions_between(self, kt_start, kt_end):
        return _buried(self._all(), kt_start, kt_end)

    def snapshot_pin(self) -> str:
        return _pin(self._all())
