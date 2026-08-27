from __future__ import annotations

import json

import pytest

from finance_quant.trader.session import (
    SessionJournal,
    SessionReceiptError,
    build_session_receipt,
    validate_session_chain,
)

LEAN_COMMIT = "185c691b89f28bd68e48d53c02147415134975f0"


def _h(ch: str) -> str:
    return ch * 64


def _receipt(number: int, *, parent: str | None, initial: str, terminal: str):
    return build_session_receipt(
        session_id=f"session-{number}",
        session_number=number,
        parent_receipt_hash=parent,
        initial_state_hash=initial,
        terminal_state_hash=terminal,
        input_hash=_h("1"),
        strategy_hash=_h("2"),
        risk_hash=_h("3"),
        execution_hash=_h("4"),
        runtime="LEAN",
        runtime_commit=LEAN_COMMIT,
        authority="NONE",
        status="COMPLETE",
    )


def test_fq_prop_025_session_chain_requires_exact_continuity(tmp_path):
    first = _receipt(1, parent=None, initial=_h("a"), terminal=_h("b"))
    second = _receipt(2, parent=first.receipt_hash, initial=first.terminal_state_hash, terminal=_h("c"))
    validate_session_chain(None, first)
    validate_session_chain(first, second)

    wrong_parent = _receipt(2, parent=_h("d"), initial=first.terminal_state_hash, terminal=_h("c"))
    with pytest.raises(SessionReceiptError, match="parent"):
        validate_session_chain(first, wrong_parent)
    wrong_state = _receipt(2, parent=first.receipt_hash, initial=_h("e"), terminal=_h("c"))
    with pytest.raises(SessionReceiptError, match="initial state"):
        validate_session_chain(first, wrong_state)

    journal = SessionJournal(tmp_path / "sessions.jsonl")
    journal.append(first)
    journal.append(second)
    assert [r.receipt_hash for r in journal.read_all()] == [first.receipt_hash, second.receipt_hash]


def test_fq_prop_026_receipt_hash_is_deterministic():
    first = _receipt(1, parent=None, initial=_h("a"), terminal=_h("b"))
    second = _receipt(1, parent=None, initial=_h("a"), terminal=_h("b"))
    assert first == second
    assert first.receipt_hash == second.receipt_hash


def test_tampered_journal_fails_closed(tmp_path):
    receipt = _receipt(1, parent=None, initial=_h("a"), terminal=_h("b"))
    path = tmp_path / "sessions.jsonl"
    journal = SessionJournal(path)
    journal.append(receipt)
    value = json.loads(path.read_text(encoding="utf-8"))
    value["terminal_state_hash"] = _h("f")
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    with pytest.raises(SessionReceiptError, match="receipt_hash mismatch"):
        journal.read_all()


def test_duplicate_session_identity_is_rejected(tmp_path):
    receipt = _receipt(1, parent=None, initial=_h("a"), terminal=_h("b"))
    journal = SessionJournal(tmp_path / "sessions.jsonl")
    journal.append(receipt)
    with pytest.raises(SessionReceiptError, match="duplicate session_id"):
        journal.append(receipt)
