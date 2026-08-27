"""Fail closed on A2 Autonomous Trader v0 contract/state drift."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "contracts" / "project" / "project-state.json"
ASSURANCE = ROOT / "contracts" / "assurance" / "capability-assurance-v1.json"
DECISION = ROOT / "contracts" / "execution" / "a1-runtime-decision-v1.json"
A2 = ROOT / "contracts" / "trading" / "autonomous-trader-v0.json"
PLAN = ROOT / "docs" / "plans" / "A2_AUTONOMOUS_TRADER_V0.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    for path in (PROJECT, ASSURANCE, DECISION, A2, PLAN):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing/empty A2 artifact: {path.relative_to(ROOT)}")
    if errors:
        return errors

    project = _load(PROJECT)
    assurance = _load(ASSURANCE)
    decision = _load(DECISION)
    contract = _load(A2)

    if project.get("active_issue") != 16 or project.get("assurance_phase") != "A2":
        errors.append("durable project state must point to issue #16 / A2")
    if project.get("current_capability") != "AUTONOMOUS_TRADER_V0":
        errors.append("current capability must be AUTONOMOUS_TRADER_V0")
    authority = project.get("authority", {})
    if authority.get("trading") != "NONE":
        errors.append("A2 build authority must remain NONE before HITL promotion")
    if authority.get("paper_trading_enabled") is not False:
        errors.append("unattended paper must remain disabled before A2 promotion")
    if authority.get("live_capital_enabled") is not False:
        errors.append("live capital must remain disabled")

    phase = next((p for p in assurance.get("phases", []) if p.get("id") == "A2"), None)
    if phase is None or phase.get("completion_status") != "IN_PROGRESS":
        errors.append("A2 assurance phase must be IN_PROGRESS")
    required = set(phase.get("required", [])) if phase else set()
    for technique in (
        "SDD", "PDD", "STATIC_IR", "UNIT_REGRESSION", "PROPERTY_STATEFUL",
        "HIDDEN_ACCEPTANCE", "MUTATION", "DIFFERENTIAL", "METAMORPHIC",
        "DETERMINISM", "CLEAN_ENV", "CHAOS_FAULT", "HITL_PROMOTION",
    ):
        if technique not in required:
            errors.append(f"A2 assurance missing required technique {technique}")

    selected = contract.get("selected_runtime", {})
    if selected.get("name") != decision.get("selected_primary_runtime"):
        errors.append("A2 runtime must match the A1 selected primary runtime")
    if selected.get("source_commit") != decision.get("selected_primary_source_commit"):
        errors.append("A2 runtime pin must match the A1 selected source commit")
    if selected.get("disposition") != "ADOPT_WITH_CONSTRAINTS":
        errors.append("A2 must preserve LEAN ADOPT_WITH_CONSTRAINTS")

    c_authority = contract.get("authority", {})
    if c_authority.get("build_authority") != "NONE":
        errors.append("A2 contract build authority must be NONE")
    if c_authority.get("unattended_paper_enabled") is not False:
        errors.append("A2 contract must not pre-authorize unattended paper")
    if c_authority.get("live_capital_enabled") is not False:
        errors.append("A2 contract must not authorize live capital")
    if c_authority.get("brokerage_credentials_allowed") is not False:
        errors.append("A2 contract must forbid brokerage credentials")
    if c_authority.get("hitl_promotion_required") is not True:
        errors.append("A2 contract must require HITL promotion")

    expected_props = {f"FQ-PROP-{number:03d}" for number in range(23, 30)}
    if set(contract.get("properties", [])) != expected_props:
        errors.append("A2 contract property set must be FQ-PROP-023..029")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("A2 contract validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("A2 contract validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
