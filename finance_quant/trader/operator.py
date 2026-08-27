"""Read-only operator evidence projection for A2."""
from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .evidence import ReplayableAccountStore


@dataclass(frozen=True)
class OperatorEvent:
    event_type: str
    session_id: str
    session_number: int
    receipt_hash: str
    status: str
    runtime: str
    authority: str


def build_operator_events(store: ReplayableAccountStore) -> list[OperatorEvent]:
    return [
        OperatorEvent(
            event_type="SESSION_RECEIPT",
            session_id=str(item["session_id"]),
            session_number=int(item["session_number"]),
            receipt_hash=str(item["receipt_hash"]),
            status=str(item["status"]),
            runtime=str(item["runtime"]),
            authority=str(item["authority"]),
        )
        for item in store.session_receipts()
    ]


def build_operator_snapshot(
    store: ReplayableAccountStore,
    project_authority: Mapping[str, object],
) -> dict[str, Any]:
    state_hash = store.state_hash()
    evidence = store.session_evidence()
    snapshot = {
        "schema_version": "1.0.0",
        "issue": 16,
        "phase": "A2",
        "mode": "READ_ONLY_OPERATOR_EVIDENCE",
        "authority": dict(project_authority),
        "account_state_hash": state_hash,
        "account": store.authoritative_state(),
        "session_receipts": store.session_receipts(),
        "evidence_sessions": [
            {"session_id": item["session_id"], "session_number": item["session_number"]}
            for item in evidence
        ],
        "events": [asdict(item) for item in build_operator_events(store)],
        "commands": [],
    }
    if store.state_hash() != state_hash:
        raise RuntimeError("operator snapshot mutated authoritative account state")
    return snapshot


def render_operator_html(snapshot: Mapping[str, Any]) -> str:
    payload = html.escape(json.dumps(dict(snapshot), indent=2, sort_keys=True))
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>A2 Operator Evidence</title></head>"
        "<body><h1>Autonomous Trader v0 — read-only evidence</h1>"
        "<p>No execution, promotion, brokerage, or capital command is exposed by this view.</p>"
        f"<pre>{payload}</pre></body></html>"
    )
