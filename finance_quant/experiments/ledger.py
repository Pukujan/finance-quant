"""Append-only ExperimentLedger facade over SQLite for V0.

MLflow is deliberately NOT called directly by research code. This facade owns the
minimum reproducibility contract and append-only run truth; an MLflow adapter can
mirror committed rows later without changing the contract.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    INVALID = "invalid"


class LedgerError(ValueError):
    pass


def _hash(payload: object) -> str:
    return hashlib.blake2b(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(), digest_size=32).hexdigest()


@dataclass(frozen=True)
class RunSpec:
    """Required fields from spike #4 sec. 3. No partial run specifications."""
    experiment_id: str
    code_sha: str
    env_lock_hash: str
    dataset_manifest_hash: str
    feature_ir_hash: str
    model_config_hash: str
    seeds: tuple[int, ...]
    split_policy_ref: str
    cost_model_ref: str
    agent_origin: str = "human"
    parent_run_id: Optional[str] = None
    hardware_profile: str = "unspecified"

    def __post_init__(self) -> None:
        required = (self.experiment_id, self.code_sha, self.env_lock_hash,
                    self.dataset_manifest_hash, self.feature_ir_hash,
                    self.model_config_hash, self.split_policy_ref, self.cost_model_ref)
        if not all(required) or not self.seeds:
            raise LedgerError("all reproducibility fields and at least one seed are required")

    @property
    def idempotency_key(self) -> str:
        return _hash(asdict(self))


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    spec: RunSpec
    status: RunStatus
    created_at: float
    completed_at: Optional[float] = None
    metrics: tuple[tuple[str, float], ...] = ()
    artifacts: tuple[tuple[str, str], ...] = ()
    error_class: Optional[str] = None


_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS runs(
  run_id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL, spec_json TEXT NOT NULL,
  status TEXT NOT NULL, created_at REAL NOT NULL, completed_at REAL,
  metrics_json TEXT NOT NULL, artifacts_json TEXT NOT NULL, error_class TEXT
);
"""


class ExperimentLedger:
    """Only writer for experiment truth. No delete/update API is intentionally exposed."""

    def __init__(self, path: str | Path):
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def begin(self, spec: RunSpec) -> RunRecord:
        """Idempotent: same spec returns exactly the same authority record."""
        key = spec.idempotency_key
        with self._lock:
            row = self._db.execute("SELECT * FROM runs WHERE idempotency_key=?", (key,)).fetchone()
            if row:
                return _decode(row)
            run_id = _hash({"run": key})
            now = time.time()
            self._db.execute(
                "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)",
                (run_id, key, json.dumps(asdict(spec), sort_keys=True), RunStatus.RUNNING.value,
                 now, None, "[]", "[]", None),
            )
            self._db.commit()
            return RunRecord(run_id, spec, RunStatus.RUNNING, now)

    def finalize(self, run_id: str, status: RunStatus, metrics: dict[str, float] | None = None,
                 artifacts: dict[str, str] | None = None, error_class: str | None = None) -> RunRecord:
        if status is RunStatus.RUNNING:
            raise LedgerError("cannot finalize as running")
        with self._lock:
            row = self._db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                raise LedgerError("unknown run")
            existing = _decode(row)
            if existing.status is not RunStatus.RUNNING:
                if existing.status == status and existing.metrics == tuple(sorted((metrics or {}).items())):
                    return existing  # idempotent finalization receipt
                raise LedgerError("terminal run records are immutable")
            if status is RunStatus.SUCCESS and error_class:
                raise LedgerError("success cannot carry error class")
            now = time.time()
            m, a = tuple(sorted((metrics or {}).items())), tuple(sorted((artifacts or {}).items()))
            self._db.execute(
                "UPDATE runs SET status=?, completed_at=?, metrics_json=?, artifacts_json=?, error_class=?"
                " WHERE run_id=?",
                (status.value, now, json.dumps(m), json.dumps(a), error_class, run_id),
            )
            self._db.commit()
            return RunRecord(run_id, existing.spec, status, existing.created_at, now, m, a, error_class)

    def get(self, run_id: str) -> RunRecord:
        row = self._db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row: raise LedgerError("unknown run")
        return _decode(row)


def _decode(row: tuple) -> RunRecord:
    run_id, _, spec_json, status, created, completed, metrics, artifacts, error = row
    raw = json.loads(spec_json)
    raw["seeds"] = tuple(raw["seeds"])
    return RunRecord(run_id, RunSpec(**raw), RunStatus(status), created, completed,
                     tuple(tuple(x) for x in json.loads(metrics)),
                     tuple(tuple(x) for x in json.loads(artifacts)), error)
