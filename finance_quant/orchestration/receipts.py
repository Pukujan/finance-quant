"""Receipt parsing/validation at the supervisor boundary. Malformed => invalid."""
from __future__ import annotations

import json
from typing import Any

from .contracts import (Artifact, ContractError, ResultReceipt, TerminalStatus,
                        content_hash)


def parse_receipt(payload: str | bytes) -> ResultReceipt:
    try:
        raw: dict[str, Any] = json.loads(payload)
        return ResultReceipt(
            work_order_hash=str(raw["work_order_hash"]),
            retry_seq=int(raw["retry_seq"]),
            terminal_status=TerminalStatus(raw["terminal_status"]),
            worker_id=str(raw["worker_id"]),
            backend_id=str(raw["backend_id"]),
            started_at=float(raw["started_at"]),
            ended_at=float(raw["ended_at"]),
            environment_hash=str(raw["environment_hash"]),
            artifact_manifest=tuple(
                Artifact(ref=a["ref"], sha256=a["sha256"], bytes=int(a["bytes"]))
                for a in raw.get("artifact_manifest", [])
            ),
            metrics=tuple((str(k), float(v)) for k, v in raw.get("metrics", [])),
            error_class=raw.get("error_class"),
        )
    except (KeyError, TypeError, ValueError, ContractError) as exc:
        raise ContractError(f"malformed receipt: {exc}") from exc


def envelope_hash(receipt: ResultReceipt, ledger_commit_ts: float) -> str:
    """Supervisor-side envelope: worker trust never extends to self-commit."""
    return content_hash({
        "receipt": receipt.receipt_hash,
        "committed_at": ledger_commit_ts,
    })
