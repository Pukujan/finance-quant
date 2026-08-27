from __future__ import annotations

import json
from pathlib import Path

import pytest

from finance_quant.trader.authority import AuthorityError, PromotionReceipt, assert_unattended_paper_authorized

ROOT = Path(__file__).resolve().parents[1]


def test_fq_prop_029_current_project_state_cannot_run_unattended_paper():
    project = json.loads((ROOT / "contracts/project/project-state.json").read_text(encoding="utf-8"))
    with pytest.raises(AuthorityError, match="not PAPER"):
        assert_unattended_paper_authorized(project["authority"], None)


def test_hitl_receipt_alone_cannot_widen_durable_authority():
    promotion = PromotionReceipt(
        issue=16,
        phase="A2",
        decision="APPROVE",
        approved_by="human-owner",
        approved_at="2026-08-27T00:00:00Z",
        evidence_hash="a" * 64,
    )
    authority = {"trading": "NONE", "paper_trading_enabled": False, "live_capital_enabled": False}
    with pytest.raises(AuthorityError, match="not PAPER"):
        assert_unattended_paper_authorized(authority, promotion)


def test_durable_paper_authority_still_requires_explicit_a2_hitl_receipt():
    authority = {"trading": "PAPER", "paper_trading_enabled": True, "live_capital_enabled": False}
    with pytest.raises(AuthorityError, match="HITL"):
        assert_unattended_paper_authorized(authority, None)
