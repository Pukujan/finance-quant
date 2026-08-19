"""Deterministic fan-in against the expected manifest (never arrival-order dependent)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from .contracts import content_hash
from .lifecycle import (AttemptState, AttemptStore, TERMINAL_STATES)


@dataclass(frozen=True)
class FanInResult:
    manifest_hash: str
    complete: bool
    total_expected: int
    terminal_count: int
    aggregate_fingerprint: Optional[str]  # None unless complete


class PartialCampaign(RuntimeError):
    """Raised when aggregation (not just status query) is requested too early."""


def semantic_projection(receipt_json: str) -> dict:
    """The deterministic content of a receipt: identity, status, metrics, artifact
    hashes. Wall-clock times, worker ids and staging paths are deliberately excluded
    so fingerprints are comparable ACROSS runs, not just within one."""
    r = json.loads(receipt_json)
    return {
        "work_order_hash": r["work_order_hash"],
        "terminal_status": r["terminal_status"],
        "metrics": r.get("metrics", []),
        "artifact_sha256": sorted(a["sha256"] for a in r.get("artifact_manifest", [])),
    }


def campaign_fingerprint(manifest_hash: str, receipt_jsons: list[str]) -> str:
    projections = sorted((semantic_projection(j) for j in receipt_jsons),
                         key=lambda p: p["work_order_hash"])
    return content_hash({"manifest": manifest_hash, "results": projections})


def status(store: AttemptStore, manifest_hash: str,
           expected_attempt_ids: tuple[str, ...]) -> FanInResult:
    states = store.states(expected_attempt_ids)
    terminal = sum(1 for s in states.values() if s in TERMINAL_STATES)
    complete = len(states) == len(expected_attempt_ids) and terminal == len(expected_attempt_ids)
    fingerprint = None
    if complete:
        fingerprint = campaign_fingerprint(
            manifest_hash, store.authoritative_receipts(expected_attempt_ids)
        )
    return FanInResult(
        manifest_hash=manifest_hash,
        complete=complete,
        total_expected=len(expected_attempt_ids),
        terminal_count=terminal,
        aggregate_fingerprint=fingerprint,
    )


def deterministic_aggregate(store: AttemptStore, manifest_hash: str,
                            expected_attempt_ids: tuple[str, ...]) -> dict:
    """Aggregate only a complete campaign; result is independent of completion order."""
    st = status(store, manifest_hash, expected_attempt_ids)
    if not st.complete:
        raise PartialCampaign(
            f"{st.terminal_count}/{st.total_expected} attempts terminal"
        )
    receipts = store.authoritative_receipts(expected_attempt_ids)  # sorted by woh
    return {
        "manifest_hash": manifest_hash,
        "n_authoritative": len(receipts),
        "duplicates_superseded": len(store.duplicates()),
        "fingerprint": st.aggregate_fingerprint,
        "receipts": receipts,
    }
