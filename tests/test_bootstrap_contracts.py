from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_contract_validator_passes():
    result = subprocess.run(
        [sys.executable, "scripts/validate_bootstrap_contracts.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_project_status_is_fresh():
    result = subprocess.run(
        [sys.executable, "scripts/generate_project_status.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_assurance_ladder_has_all_phases_and_critical_gates():
    assurance = json.loads((ROOT / "contracts/assurance/capability-assurance-v1.json").read_text())
    phases = {p["id"]: p for p in assurance["phases"]}
    assert list(phases) == [f"A{i}" for i in range(9)]
    assert {"SDD", "PDD", "DETERMINISM", "CLEAN_ENV", "TLA"} <= set(phases["A0"]["required"])
    assert {"HIDDEN_ACCEPTANCE", "MUTATION", "DIFFERENTIAL", "CHAOS_FAULT"} <= set(phases["A1"]["required"])
    assert "HITL_PROMOTION" in phases["A2"]["required"]
    assert "SOAK" in phases["A3"]["required"]
    assert "TLA" in phases["A5"]["required"]
    assert "HITL_PROMOTION" in phases["A8"]["required"]


def test_bootstrap_has_no_trading_or_capital_authority():
    state = json.loads((ROOT / "contracts/project/project-state.json").read_text())
    assert state["authority"]["trading"] == "NONE"
    assert state["authority"]["paper_trading_enabled"] is False
    assert state["authority"]["live_capital_enabled"] is False
    assert state["authority"]["frontend"] == "OPERATOR_ONLY"


def test_fresh_session_read_order_is_durable():
    state = json.loads((ROOT / "contracts/project/project-state.json").read_text())
    order = state["read_order"]
    assert order[0] == "AGENTS.md"
    assert order[1] == "docs/CURRENT_STATE.md"
    assert "docs/handoffs/LATEST.md" in order
    handoff = (ROOT / "docs/handoffs/LATEST.md").read_text()
    assert "Next exact action" in handoff
    assert "#15" in handoff
