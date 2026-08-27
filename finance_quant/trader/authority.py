"""Fail-closed A2 unattended-paper capability check."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class AuthorityError(PermissionError):
    pass


@dataclass(frozen=True)
class PromotionReceipt:
    issue: int
    phase: str
    decision: str
    approved_by: str
    approved_at: str
    evidence_hash: str


def assert_unattended_paper_authorized(
    project_authority: Mapping[str, object],
    promotion: PromotionReceipt | None,
) -> None:
    """Require both durable project authority and an explicit A2 HITL approval.

    The promotion receipt cannot itself widen project authority. Durable project state
    must already have been deliberately transitioned to PAPER by the promotion path.
    """
    if project_authority.get("trading") != "PAPER":
        raise AuthorityError("durable trading authority is not PAPER")
    if project_authority.get("paper_trading_enabled") is not True:
        raise AuthorityError("paper trading is disabled in durable project state")
    if project_authority.get("live_capital_enabled") is not False:
        raise AuthorityError("A2 cannot authorize live capital")
    if promotion is None:
        raise AuthorityError("A2 HITL promotion receipt is required")
    if promotion.issue != 16 or promotion.phase != "A2" or promotion.decision != "APPROVE":
        raise AuthorityError("promotion receipt does not authorize A2 unattended paper")
    if not promotion.approved_by or not promotion.approved_at or len(promotion.evidence_hash) != 64:
        raise AuthorityError("promotion receipt is incomplete")
