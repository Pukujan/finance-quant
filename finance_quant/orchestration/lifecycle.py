"""Attempt state machine + SQLite WAL attempt ledger (sole writer: supervisor).

Invariants carried by construction (issue #10):
  1. attempt row exists before compute starts (issue() is synchronous, before spawn)
  2. terminal outcome for every allocated attempt (state machine has only the five
     contracted terminals; supervisor commits, workers never write directly)
  3. failures cannot disappear (no DELETE anywhere in this module)
  4. retry idempotency (authoritative_results keyed by work_order_hash)
  5. duplicate receipts cannot fork authority (INSERT-or-classify-duplicate)
"""
from __future__ import annotations

import sqlite3
import time
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

from .contracts import ResultReceipt, TerminalStatus, WorkOrder, content_hash


class AttemptState(str, Enum):
    ISSUED = "issued"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CRASHED = "crashed"


TERMINAL_STATES = frozenset(
    {AttemptState.COMPLETED, AttemptState.REJECTED, AttemptState.FAILED,
     AttemptState.CANCELLED, AttemptState.CRASHED}
)

_TERMINAL_BY_STATUS = {
    TerminalStatus.COMPLETED: AttemptState.COMPLETED,
    TerminalStatus.REJECTED: AttemptState.REJECTED,
    TerminalStatus.FAILED: AttemptState.FAILED,
    TerminalStatus.CANCELLED: AttemptState.CANCELLED,
    TerminalStatus.CRASHED: AttemptState.CRASHED,
}

_ALLOWED = {
    AttemptState.ISSUED: {AttemptState.QUEUED, AttemptState.CANCELLED},
    AttemptState.QUEUED: {AttemptState.RUNNING, AttemptState.CANCELLED},
    AttemptState.RUNNING: set(TERMINAL_STATES),
}
for _t in TERMINAL_STATES:
    _ALLOWED[_t] = set()


class LifecycleError(RuntimeError):
    pass


class CommitOutcome(str, Enum):
    COMMITTED = "committed"
    DUPLICATE = "superseded_duplicate"
    INVALID = "invalid"


_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS attempts(
  work_order_hash TEXT NOT NULL,
  retry_seq       INTEGER NOT NULL,
  state           TEXT NOT NULL,
  work_order_json TEXT NOT NULL,
  created_at      REAL NOT NULL,
  updated_at      REAL NOT NULL,
  error_class     TEXT,
  PRIMARY KEY(work_order_hash, retry_seq)
);
CREATE TABLE IF NOT EXISTS authoritative_results(
  work_order_hash TEXT PRIMARY KEY,
  retry_seq       INTEGER NOT NULL,
  receipt_json    TEXT NOT NULL,
  receipt_hash    TEXT NOT NULL,
  committed_at    REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS duplicate_receipts(
  receipt_hash    TEXT PRIMARY KEY,
  work_order_hash TEXT NOT NULL,
  retry_seq       INTEGER NOT NULL,
  receipt_json    TEXT NOT NULL,
  observed_at     REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS manifests(
  manifest_hash   TEXT PRIMARY KEY,
  campaign_id     TEXT NOT NULL,
  manifest_json   TEXT NOT NULL
);
"""


class AttemptStore:
    """Single-writer attempt ledger. Thread-safe via a lock held by callers' discipline;
    V0 scheduler is single-process so a module-level write transaction suffices."""

    def __init__(self, path: str | Path):
        self._path = str(path)
        self._db = sqlite3.connect(self._path, isolation_level=None)  # autocommit; explicit BEGIN below
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    # --- manifest projection -------------------------------------------------
    def project_manifest(self, campaign_id: str, manifest_hash: str,
                         manifest_json: str) -> None:
        self._db.execute(
            "INSERT OR IGNORE INTO manifests VALUES (?,?,?)",
            (manifest_hash, campaign_id, manifest_json),
        )

    # --- issuance ------------------------------------------------------------
    def issue(self, work_order: WorkOrder, retry_seq: int = 0) -> bool:
        """Returns True if newly created. Idempotent for identical (woh, retry_seq)."""
        now = time.time()
        cur = self._db.execute(
            "INSERT OR IGNORE INTO attempts"
            "(work_order_hash, retry_seq, state, work_order_json, created_at, updated_at)"
            " VALUES (?,?,?,?,?,?)",
            (work_order.work_order_hash, retry_seq, AttemptState.ISSUED.value,
             work_order_to_json(work_order), now, now),
        )
        return cur.rowcount == 1

    def _state_of(self, woh: str, retry_seq: int) -> Optional[AttemptState]:
        row = self._db.execute(
            "SELECT state FROM attempts WHERE work_order_hash=? AND retry_seq=?",
            (woh, retry_seq),
        ).fetchone()
        return AttemptState(row[0]) if row else None

    def _transition(self, woh: str, retry_seq: int, to: AttemptState,
                    error_class: Optional[str] = None) -> None:
        cur = self._state_of(woh, retry_seq)
        if cur is None:
            raise LifecycleError(f"unknown attempt {woh}:{retry_seq}")
        if to not in _ALLOWED[cur]:
            raise LifecycleError(f"illegal transition {cur.value} -> {to.value}")
        self._db.execute(
            "UPDATE attempts SET state=?, updated_at=?, error_class=COALESCE(?, error_class)"
            " WHERE work_order_hash=? AND retry_seq=?",
            (to.value, time.time(), error_class, woh, retry_seq),
        )

    def mark_queued(self, woh: str, retry_seq: int = 0) -> None:
        self._transition(woh, retry_seq, AttemptState.QUEUED)

    def mark_running(self, woh: str, retry_seq: int = 0) -> None:
        self._transition(woh, retry_seq, AttemptState.RUNNING)

    def cancel(self, woh: str, retry_seq: int = 0) -> None:
        state = self._state_of(woh, retry_seq)
        if state in (AttemptState.ISSUED, AttemptState.QUEUED):
            self._transition(woh, retry_seq, AttemptState.CANCELLED)
        elif state is AttemptState.RUNNING:
            raise LifecycleError("cancellation of RUNNING goes through the backend")

    # --- receipt commit (the authority boundary) -----------------------------
    def commit_receipt(self, receipt: ResultReceipt) -> CommitOutcome:
        woh, seq = receipt.work_order_hash, receipt.retry_seq
        state = self._state_of(woh, seq)
        if state is not AttemptState.RUNNING:
            return CommitOutcome.INVALID
        terminal = _TERMINAL_BY_STATUS[receipt.terminal_status]
        receipt_json = receipt_to_json(receipt)
        now = time.time()

        self._db.execute("BEGIN IMMEDIATE")
        try:
            self._db.execute(
                "UPDATE attempts SET state=?, updated_at=?, error_class=COALESCE(?, error_class)"
                " WHERE work_order_hash=? AND retry_seq=?",
                (terminal.value, now, receipt.error_class, woh, seq),
            )
            if receipt.terminal_status is TerminalStatus.COMPLETED:
                cur = self._db.execute(
                    "INSERT OR IGNORE INTO authoritative_results VALUES (?,?,?,?,?)",
                    (woh, seq, receipt_json, receipt.receipt_hash, now),
                )
                if cur.rowcount == 0:
                    self._db.execute(
                        "INSERT OR IGNORE INTO duplicate_receipts VALUES (?,?,?,?,?)",
                        (receipt.receipt_hash, woh, seq, receipt_json, now),
                    )
                    outcome = CommitOutcome.DUPLICATE
                else:
                    outcome = CommitOutcome.COMMITTED
            else:
                outcome = CommitOutcome.COMMITTED
            self._db.execute("COMMIT")
        except Exception:
            self._db.execute("ROLLBACK")
            raise
        return outcome

    def supervisor_crash(self, woh: str, retry_seq: int, error_class: str) -> None:
        """Supervisor-only terminal commit for dead/timed-out workers."""
        if self._state_of(woh, retry_seq) is AttemptState.RUNNING:
            self._transition(woh, retry_seq, AttemptState.CRASHED, error_class)

    # --- retry ---------------------------------------------------------------
    def next_retry_seq(self, woh: str) -> int:
        row = self._db.execute(
            "SELECT MAX(retry_seq) FROM attempts WHERE work_order_hash=?", (woh,)
        ).fetchone()
        return (row[0] if row[0] is not None else -1) + 1

    def last_state(self, woh: str) -> Optional[AttemptState]:
        row = self._db.execute(
            "SELECT state FROM attempts WHERE work_order_hash=? ORDER BY retry_seq DESC LIMIT 1",
            (woh,),
        ).fetchone()
        return AttemptState(row[0]) if row else None

    # --- queries for fan-in ----------------------------------------------------
    def states(self, wohs: Iterable[str]) -> dict[str, AttemptState]:
        out: dict[str, AttemptState] = {}
        for woh in wohs:
            row = self._db.execute(
                "SELECT state FROM attempts WHERE work_order_hash=?"
                " ORDER BY retry_seq DESC LIMIT 1",
                (woh,),
            ).fetchone()
            if row:
                out[woh] = AttemptState(row[0])
        return out

    def authoritative_receipts(self, wohs: Iterable[str]) -> list[str]:
        woh_list = list(wohs)
        if not woh_list:
            return []
        placeholders = ",".join("?" for _ in woh_list)
        rows = self._db.execute(
            "SELECT receipt_json FROM authoritative_results"
            f" WHERE work_order_hash IN ({placeholders}) ORDER BY work_order_hash",
            woh_list,
        ).fetchall()
        return [r[0] for r in rows]

    def duplicates(self) -> list[str]:
        return [r[0] for r in self._db.execute(
            "SELECT receipt_hash FROM duplicate_receipts ORDER BY observed_at"
        )]


# --- serialization helpers (kept here to keep contracts.py dependency-free of io) --
def work_order_to_json(wo: WorkOrder) -> str:
    from .contracts import canonical_json
    return canonical_json(wo).decode("utf-8")


def receipt_to_json(r: ResultReceipt) -> str:
    from .contracts import canonical_json
    return canonical_json(r).decode("utf-8")


def campaign_fingerprint(manifest_hash: str, receipt_jsons: list[str]) -> str:
    """Deterministic campaign fingerprint: completion order cannot change it."""
    return content_hash({"manifest": manifest_hash, "receipts": sorted(receipt_jsons)})
