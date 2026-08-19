"""Deterministic fan-in against the expected manifest (never arrival-order dependent)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .lifecycle import (AttemptState, AttemptStore, TERMINAL_STATES,
                        campaign_fingerprint)


@dataclass(frozen=True)
class FanInResult:
    manifest_hash: str
    complete: bool
    total_expected: int
    terminal_count: int
    aggregate_fingerprint: Optional[str]  # None unless complete


class PartialCampaign(RuntimeError):
    """Raised when aggregation (not just status query) is requested too early."""


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
