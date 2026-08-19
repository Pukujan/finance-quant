"""JSONL + manifest PIT candidate (spike #2 constrained bake-off list).

No pandas/pyarrow required. Each put appends a canonical JSON line; snapshot_pin
hashes the full history. as_of uses the same visibility rule as MemoryGoldStore.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .model import BitemporalRecord
from .store import _pin, _visible, _buried


class ManifestJsonlStore:
    """Append-only file store. Corrections never rewrite prior lines."""

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[BitemporalRecord] = []
        if self._path.exists():
            for line in self._path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self._records.append(_from_json(json.loads(line)))

    def put(self, record: BitemporalRecord) -> None:
        self._records.append(record)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(record.canonical().decode("utf-8") + "\n")

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


def _from_json(raw: dict) -> BitemporalRecord:
    return BitemporalRecord(
        namespace=raw["namespace"],
        instrument_id=raw["instrument_id"],
        vt=raw["vt"],
        kt=raw["kt"],
        payload=raw["payload"],
        source=raw["source"],
        revision=raw["revision"],
        ingest_run_id=raw.get("ingest_run_id", "fixture"),
        superseded_by=raw.get("superseded_by"),
    )
