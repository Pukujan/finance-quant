"""Atomic replay evidence bound to authoritative A2 SessionReceipts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .account import AccountInvariantError, VirtualAccountStore
from .execution import commit_lean_session
from .session import SessionReceipt


class EvidenceInvariantError(ValueError):
    pass


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ReplayableAccountStore(VirtualAccountStore):
    """VirtualAccountStore whose SessionReceipt insert also persists exact replay evidence."""

    def __init__(self, path: str | Path, *, initial_cash: object | None = None) -> None:
        super().__init__(path, initial_cash=initial_cash)
        self._pending_evidence: dict[str, Any] | None = None
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS session_evidence (
                session_number INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL UNIQUE,
                fixture_json TEXT NOT NULL,
                execution_json TEXT NOT NULL,
                strategy_hash TEXT NOT NULL,
                risk_hash TEXT NOT NULL,
                runtime_commit TEXT NOT NULL,
                FOREIGN KEY(session_number) REFERENCES session_receipts(session_number)
            )
            """
        )
        self._conn.commit()

    def stage_session_evidence(
        self,
        *,
        session_id: str,
        fixture: Mapping[str, Any],
        execution_receipt: Mapping[str, Any],
        strategy_hash: str,
        risk_hash: str,
        runtime_commit: str,
    ) -> None:
        if self._pending_evidence is not None:
            raise EvidenceInvariantError("session evidence is already staged")
        self._pending_evidence = {
            "session_id": str(session_id),
            "fixture_json": _canonical(dict(fixture)),
            "execution_json": _canonical(dict(execution_receipt)),
            "strategy_hash": str(strategy_hash),
            "risk_hash": str(risk_hash),
            "runtime_commit": str(runtime_commit),
        }

    def clear_staged_evidence(self) -> None:
        self._pending_evidence = None

    def _insert_staged_evidence(self, receipt: SessionReceipt) -> None:
        pending = self._pending_evidence
        if pending is None:
            raise AccountInvariantError("authoritative session receipt requires staged replay evidence")
        checks = {
            "session_id": receipt.session_id,
            "strategy_hash": receipt.strategy_hash,
            "risk_hash": receipt.risk_hash,
            "runtime_commit": receipt.runtime_commit,
        }
        for key, expected in checks.items():
            if pending[key] != expected:
                raise AccountInvariantError(f"staged replay evidence {key} mismatch")
        execution = json.loads(pending["execution_json"])
        fixture = json.loads(pending["fixture_json"])
        if execution.get("receipt_hash") != receipt.execution_hash:
            raise AccountInvariantError("staged execution receipt hash mismatch")
        if execution.get("input_hash") != receipt.input_hash:
            raise AccountInvariantError("staged execution input hash mismatch")
        if fixture.get("fixture_id") != execution.get("fixture_id"):
            raise AccountInvariantError("staged fixture/execution identity mismatch")
        self._conn.execute(
            """INSERT INTO session_evidence(
                session_number,session_id,fixture_json,execution_json,strategy_hash,risk_hash,runtime_commit
            ) VALUES(?,?,?,?,?,?,?)""",
            (
                receipt.session_number,
                receipt.session_id,
                pending["fixture_json"],
                pending["execution_json"],
                pending["strategy_hash"],
                pending["risk_hash"],
                pending["runtime_commit"],
            ),
        )

    def append_session_receipt(self, receipt: object) -> bool:
        current = receipt if isinstance(receipt, SessionReceipt) else SessionReceipt.from_dict(dict(receipt))
        inserted = super().append_session_receipt(current)
        if inserted:
            self._insert_staged_evidence(current)
        return inserted

    def get_session_evidence(self, session_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM session_evidence WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return {
            "session_number": int(row["session_number"]),
            "session_id": str(row["session_id"]),
            "fixture": json.loads(str(row["fixture_json"])),
            "execution_receipt": json.loads(str(row["execution_json"])),
            "strategy_hash": str(row["strategy_hash"]),
            "risk_hash": str(row["risk_hash"]),
            "runtime_commit": str(row["runtime_commit"]),
        }

    def session_evidence(self) -> list[dict[str, Any]]:
        return [
            self.get_session_evidence(str(row["session_id"]))
            for row in self._conn.execute("SELECT session_id FROM session_evidence ORDER BY session_number").fetchall()
        ]


def commit_replayable_session(
    store: ReplayableAccountStore,
    receipt: Mapping[str, Any],
    fixture: Mapping[str, Any],
    *,
    session_id: str,
    strategy_hash: str,
    risk_hash: str,
    runtime_commit: str,
) -> SessionReceipt:
    store.stage_session_evidence(
        session_id=session_id,
        fixture=fixture,
        execution_receipt=receipt,
        strategy_hash=strategy_hash,
        risk_hash=risk_hash,
        runtime_commit=runtime_commit,
    )
    try:
        result = commit_lean_session(
            store,
            receipt,
            fixture,
            session_id=session_id,
            strategy_hash=strategy_hash,
            risk_hash=risk_hash,
            runtime_commit=runtime_commit,
        )
        evidence = store.get_session_evidence(session_id)
        if evidence is None:
            raise EvidenceInvariantError("committed session lacks authoritative replay evidence")
        if evidence["execution_receipt"] != dict(receipt) or evidence["fixture"] != dict(fixture):
            raise EvidenceInvariantError("stored replay evidence differs from committed evidence")
        return result
    finally:
        store.clear_staged_evidence()


def replay_authoritative_store(source_path: str | Path, target_path: str | Path) -> dict[str, Any]:
    target = Path(target_path)
    if target.exists():
        raise EvidenceInvariantError("replay target must not already exist")
    with ReplayableAccountStore(source_path) as source:
        receipts = source.session_receipts()
        if not receipts:
            raise EvidenceInvariantError("source store has no sessions to replay")
        evidence = [source.get_session_evidence(str(item["session_id"])) for item in receipts]
        if any(item is None for item in evidence):
            raise EvidenceInvariantError("source store has missing replay evidence")
        first_fixture = evidence[0]["fixture"]
        with ReplayableAccountStore(target, initial_cash=first_fixture["initial_cash"]) as replay:
            replayed_hashes: list[str] = []
            for expected_raw, item in zip(receipts, evidence, strict=True):
                expected = SessionReceipt.from_dict(expected_raw)
                actual = commit_replayable_session(
                    replay,
                    item["execution_receipt"],
                    item["fixture"],
                    session_id=item["session_id"],
                    strategy_hash=item["strategy_hash"],
                    risk_hash=item["risk_hash"],
                    runtime_commit=item["runtime_commit"],
                )
                if actual != expected:
                    raise EvidenceInvariantError("replayed SessionReceipt differs from authoritative source")
                replayed_hashes.append(actual.receipt_hash)
            if replay.state_hash() != source.state_hash():
                raise EvidenceInvariantError("replay terminal account state differs from source")
            return {
                "schema_version": "1.0.0",
                "issue": 16,
                "phase": "A2",
                "session_receipt_hashes": replayed_hashes,
                "terminal_state_hash": replay.state_hash(),
                "status": "PASS",
                "authority": "NONE",
            }
