"""Optional ArcticDB PIT adapter. Skipped unless arcticdb is installed.

License constraint (spike #2): only Apache-converted versions. This adapter is a
candidate, not the V0 authority.
"""
from __future__ import annotations

from typing import Iterable

from .model import BitemporalRecord
from .store import _buried, _pin, _visible


def arcticdb_available() -> bool:
    try:
        import arcticdb  # noqa: F401
        return True
    except ImportError:
        return False


class ArcticPITStore:
    def __init__(self, uri: str = "lmdb://./.arctic-pit", lib: str = "pit"):
        import arcticdb as adb
        self._ac = adb.Arctic(uri)
        if lib not in self._ac.list_libraries():
            self._ac.create_library(lib)
        self._lib = self._ac[lib]
        self._symbol = "records"
        self._records: list[BitemporalRecord] = []

    def close(self) -> None:
        return

    def put(self, record: BitemporalRecord) -> None:
        self._records.append(record)

    def as_of(self, namespace, instruments, vt_start, vt_end, kt_bound):
        allowed = set(instruments)
        return _visible(
            (r for r in self._records if r.namespace == namespace and r.instrument_id in allowed),
            vt_start, vt_end, kt_bound,
        )

    def revisions_between(self, kt_start, kt_end):
        return _buried(self._records, kt_start, kt_end)

    def snapshot_pin(self) -> str:
        return _pin(self._records)
