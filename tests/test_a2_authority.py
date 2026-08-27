from __future__ import annotations

import json
from pathlib import Path

import pytest

from finance_quant.trader.authority import AuthorityError, PromotionReceipt, assert_unattended_paper_authorized

ROOT = Path(__file__).resolve().parents[1]


def _promotion(**overrides):
    values = {
        "issue": 16,
        "phase": "A2",
        "decision": "APPROVE",
        "approved_by": "human-owner",
        "approved_at": "2026-08-27T00:00:00Z",
        "evidence_hash": "a" * 64,
    }
    values.update(overrides)
    return PromotionReceipt(**values)


def _paper_authority(**overrides):
    values = {"trading": "PAPER", "paper_trading_enabled": True, "live_capital_enabled": False}
    values.update(overrides)
    return values


def test_fq_prop_029_current_project_state_cannot_run_unattended_paper():
    project = json.loads((ROOT / "contracts/project/project-state.json").read_text(encoding="utf-8"))
    with pytest.raises(AuthorityError, match="not PAPER"):
        assert_unattended_paper_authorized(project["authority"], None)


def test_hitl_receipt_alone_cannot_widen_durable_authority():
    authority = {"trading": "NONE", "paper_trading_enabled": False, "live_capital_enabled": False}
    with pytest.raises(AuthorityError, match="not PAPER"):
        assert_unattended_paper_authorized(authority, _promotion())


def test_durable_paper_authority_still_requires_explicit_a2_hitl_receipt():
    with pytest.raises(AuthorityError, match="HITL"):
        assert_unattended_paper_authorized(_paper_authority(), None)


def test_live_capital_is_rejected_even_with_otherwise_valid_a2_promotion():
    with pytest.raises(AuthorityError, match="live capital"):
        assert_unattended_paper_authorized(_paper_authority(live_capital_enabled=True), _promotion())


def test_wrong_phase_or_issue_promotion_is_rejected_when_project_is_paper_ready():
    with pytest.raises(AuthorityError, match="does not authorize"):
        assert_unattended_paper_authorized(_paper_authority(), _promotion(phase="A3"))
    with pytest.raises(AuthorityError, match="does not authorize"):
        assert_unattended_paper_authorized(_paper_authority(), _promotion(issue=17))


def test_complete_a2_promotion_and_durable_paper_authority_are_jointly_required():
    assert_unattended_paper_authorized(_paper_authority(), _promotion())
