"""Bitemporal record model (spike #2 decision: vt x kt semantics)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


class PitContractError(ValueError):
    pass


NAMESPACES = ("bar", "fundamental", "corporate_action", "universe", "macro")


@dataclass(frozen=True)
class BitemporalRecord:
    """One fact, two clocks. kt must always be defined (contract rule: NaT forbidden)."""
    namespace: str          # bar | fundamental | corporate_action | universe | macro
    instrument_id: str      # stable internal symbology, never vendor ticker
    vt: str                 # valid time, ISO date (day granularity at this stage)
    kt: str                 # knowledge time: first-knowable instant, ISO date
    payload: dict[str, Any]
    source: str
    revision: int
    ingest_run_id: str = "fixture"
    superseded_by: Optional[int] = None

    def __post_init__(self) -> None:
        if self.namespace not in NAMESPACES:
            raise PitContractError(f"unknown namespace {self.namespace!r}")
        if not self.vt or not self.kt:
            raise PitContractError("vt and kt are both required (NaT forbidden)")
        if self.revision < 0:
            raise PitContractError("revision must be >= 0")
        if len(self.vt) != 10 or len(self.kt) != 10:
            raise PitContractError("day-granularity ISO dates expected (YYYY-MM-DD)")

    def key(self) -> tuple:
        return (self.namespace, self.instrument_id, self.vt)

    def canonical(self) -> bytes:
        return json.dumps({
            "namespace": self.namespace, "instrument_id": self.instrument_id,
            "vt": self.vt, "kt": self.kt, "revision": self.revision,
            "payload": self.payload, "source": self.source,
            "ingest_run_id": self.ingest_run_id,
            "superseded_by": self.superseded_by,
        }, sort_keys=True, separators=(",", ":")).encode("utf-8")
