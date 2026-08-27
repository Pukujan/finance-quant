"""Immutable, hash-chained SessionReceipt evidence for A2."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class SessionReceiptError(ValueError):
    pass


def _canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_sha256(value: str, *, field: str) -> None:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise SessionReceiptError(f"{field} must be lowercase sha256")


@dataclass(frozen=True)
class SessionReceipt:
    session_id: str
    session_number: int
    parent_receipt_hash: str | None
    initial_state_hash: str
    terminal_state_hash: str
    input_hash: str
    strategy_hash: str
    risk_hash: str
    execution_hash: str
    runtime: str
    runtime_commit: str
    authority: str
    status: str
    receipt_hash: str

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value.pop("receipt_hash")
        return value

    def validate(self) -> None:
        if not self.session_id:
            raise SessionReceiptError("session_id must be non-empty")
        if self.session_number < 1:
            raise SessionReceiptError("session_number begins at 1")
        if self.parent_receipt_hash is not None:
            _require_sha256(self.parent_receipt_hash, field="parent_receipt_hash")
        for field in (
            "initial_state_hash",
            "terminal_state_hash",
            "input_hash",
            "strategy_hash",
            "risk_hash",
            "execution_hash",
            "receipt_hash",
        ):
            _require_sha256(getattr(self, field), field=field)
        if not self.runtime or not self.runtime_commit:
            raise SessionReceiptError("runtime identity must be non-empty")
        if self.authority not in {"NONE", "PAPER"}:
            raise SessionReceiptError("unsupported authority")
        if self.status not in {"COMPLETE", "FAILED", "ABORTED"}:
            raise SessionReceiptError("unsupported session status")
        if self.receipt_hash != _canonical_hash(self.payload()):
            raise SessionReceiptError("receipt_hash mismatch")

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SessionReceipt":
        expected = set(cls.__dataclass_fields__)
        if set(value) != expected:
            raise SessionReceiptError("session receipt schema mismatch")
        receipt = cls(**value)
        receipt.validate()
        return receipt


def build_session_receipt(
    *,
    session_id: str,
    session_number: int,
    parent_receipt_hash: str | None,
    initial_state_hash: str,
    terminal_state_hash: str,
    input_hash: str,
    strategy_hash: str,
    risk_hash: str,
    execution_hash: str,
    runtime: str,
    runtime_commit: str,
    authority: str = "NONE",
    status: str = "COMPLETE",
) -> SessionReceipt:
    payload = {
        "session_id": session_id,
        "session_number": session_number,
        "parent_receipt_hash": parent_receipt_hash,
        "initial_state_hash": initial_state_hash,
        "terminal_state_hash": terminal_state_hash,
        "input_hash": input_hash,
        "strategy_hash": strategy_hash,
        "risk_hash": risk_hash,
        "execution_hash": execution_hash,
        "runtime": runtime,
        "runtime_commit": runtime_commit,
        "authority": authority,
        "status": status,
    }
    receipt = SessionReceipt(receipt_hash=_canonical_hash(payload), **payload)
    receipt.validate()
    return receipt


def validate_session_chain(previous: SessionReceipt | None, current: SessionReceipt) -> None:
    current.validate()
    if previous is None:
        if current.session_number != 1 or current.parent_receipt_hash is not None:
            raise SessionReceiptError("first session must be number 1 with no parent")
        return
    previous.validate()
    if current.session_number != previous.session_number + 1:
        raise SessionReceiptError("session number is not contiguous")
    if current.parent_receipt_hash != previous.receipt_hash:
        raise SessionReceiptError("parent receipt hash mismatch")
    if current.initial_state_hash != previous.terminal_state_hash:
        raise SessionReceiptError("session initial state does not match prior terminal state")


class SessionJournal:
    """Append-only JSONL receipt journal. No update/delete operation is exposed."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_all(self) -> list[SessionReceipt]:
        if not self.path.exists():
            return []
        receipts: list[SessionReceipt] = []
        previous: SessionReceipt | None = None
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                raise SessionReceiptError(f"blank journal line: {line_number}")
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SessionReceiptError(f"invalid journal JSON at line {line_number}") from exc
            if not isinstance(value, dict):
                raise SessionReceiptError("journal entry must be a JSON object")
            receipt = SessionReceipt.from_dict(value)
            validate_session_chain(previous, receipt)
            receipts.append(receipt)
            previous = receipt
        return receipts

    def append(self, receipt: SessionReceipt) -> None:
        receipts = self.read_all()
        if any(item.session_id == receipt.session_id for item in receipts):
            raise SessionReceiptError("duplicate session_id")
        previous = receipts[-1] if receipts else None
        validate_session_chain(previous, receipt)
        serialized = json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
