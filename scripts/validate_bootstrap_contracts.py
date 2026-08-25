"""Fail closed on bootstrap project-state and phase-assurance contract drift."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "contracts" / "project" / "project-state.json"
ASSURANCE = ROOT / "contracts" / "assurance" / "capability-assurance-v1.json"
PROPERTY_CATALOG = ROOT / "contracts" / "properties" / "finance-quant-properties-v1.json"

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ASSURANCE.md",
    ROOT / "docs" / "handoffs" / "LATEST.md",
    PROJECT,
    ASSURANCE,
    PROPERTY_CATALOG,
]
EXPECTED_PHASES = [f"A{i}" for i in range(9)]
EXPECTED_TECHNIQUES = {
    "SDD", "PDD", "STATIC_IR", "UNIT_REGRESSION", "PROPERTY_STATEFUL",
    "HIDDEN_ACCEPTANCE", "MUTATION", "DIFFERENTIAL", "METAMORPHIC",
    "DETERMINISM", "CLEAN_ENV", "CHAOS_FAULT", "SOAK", "TLA", "SMT",
    "LEAN4", "HITL_PROMOTION",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def validate() -> list[str]:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing/empty required bootstrap artifact: {path.relative_to(ROOT)}")

    if errors:
        return errors

    project = _load(PROJECT)
    assurance = _load(ASSURANCE)
    properties = _load(PROPERTY_CATALOG)

    if project.get("schema_version") != "1.0.0":
        errors.append("project-state schema_version must be 1.0.0")
    if project.get("architecture") != "OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM":
        errors.append("project architecture is not the OSS-first replatform")
    if project.get("active_epic") != 12:
        errors.append("active_epic must be #12 during bootstrap")
    if project.get("active_issue") != 13:
        errors.append("active_issue must be #13 until bootstrap is marked complete")
    if project.get("assurance_issue") != 14 or project.get("assurance_phase") != "A0":
        errors.append("bootstrap must be governed by issue #14 / phase A0")

    authority = project.get("authority", {})
    if authority.get("trading") != "NONE":
        errors.append("bootstrap trading authority must be NONE")
    if authority.get("paper_trading_enabled") is not False:
        errors.append("paper trading must remain disabled during bootstrap")
    if authority.get("live_capital_enabled") is not False:
        errors.append("live capital must remain disabled during bootstrap")
    if authority.get("frontend") != "OPERATOR_ONLY":
        errors.append("frontend authority must be OPERATOR_ONLY")

    read_order = project.get("read_order", [])
    for required in ("AGENTS.md", "docs/CURRENT_STATE.md", "docs/handoffs/LATEST.md"):
        if required not in read_order:
            errors.append(f"project-state read_order missing {required}")
    if not str(project.get("next_exact_action", "")).strip():
        errors.append("project-state next_exact_action must be non-empty")

    techniques = set(assurance.get("techniques", {}))
    missing_techniques = EXPECTED_TECHNIQUES - techniques
    if missing_techniques:
        errors.append(f"assurance technique vocabulary missing {sorted(missing_techniques)}")

    phases = assurance.get("phases", [])
    phase_ids = [p.get("id") for p in phases]
    if phase_ids != EXPECTED_PHASES:
        errors.append(f"assurance phases must be ordered {EXPECTED_PHASES}; got {phase_ids}")

    phase_map = {p["id"]: p for p in phases if "id" in p}
    minimums = {
        "A0": {"SDD", "PDD", "UNIT_REGRESSION", "DETERMINISM", "CLEAN_ENV", "TLA"},
        "A1": {"PROPERTY_STATEFUL", "HIDDEN_ACCEPTANCE", "MUTATION", "DIFFERENTIAL", "METAMORPHIC", "CHAOS_FAULT"},
        "A2": {"HIDDEN_ACCEPTANCE", "MUTATION", "CHAOS_FAULT", "HITL_PROMOTION"},
        "A3": {"SOAK", "CHAOS_FAULT"},
        "A4": {"HIDDEN_ACCEPTANCE", "DIFFERENTIAL", "METAMORPHIC"},
        "A5": {"TLA", "HITL_PROMOTION"},
        "A6": {"HIDDEN_ACCEPTANCE", "HITL_PROMOTION"},
        "A7": {"DIFFERENTIAL", "HITL_PROMOTION"},
        "A8": {"SOAK", "TLA", "HITL_PROMOTION"},
    }
    for phase_id, required in minimums.items():
        actual = set(phase_map.get(phase_id, {}).get("required", []))
        missing = required - actual
        if missing:
            errors.append(f"{phase_id} missing required assurance techniques {sorted(missing)}")

    mutation = assurance.get("mutation_policy", {})
    if mutation.get("critical_minimum_valid_mutant_kill_rate", 0) < 0.98:
        errors.append("critical mutation threshold must be >= 0.98")
    if mutation.get("high_minimum_valid_mutant_kill_rate", 0) < 0.95:
        errors.append("high mutation threshold must be >= 0.95")
    if mutation.get("critical_invariant_bypass_survivor_allowed") is not False:
        errors.append("critical invariant-bypass surviving mutants must be forbidden")

    t3 = [p for p in properties.get("properties", []) if p.get("status") == "active" and p.get("tier") == "T3"]
    if not t3:
        errors.append("property catalog has no active T3 property")
    for prop in t3:
        ref = prop.get("tla_ref")
        if not ref:
            errors.append(f"{prop.get('property_id')} is T3 without tla_ref")
        elif not (ROOT / ref).is_file():
            errors.append(f"{prop.get('property_id')} TLA artifact missing: {ref}")

    agents = (ROOT / "AGENTS.md").read_text()
    for token in ("docs/CURRENT_STATE.md", "docs/handoffs/LATEST.md", "HITL", "TLA", "holdout"):
        if token.lower() not in agents.lower():
            errors.append(f"AGENTS.md missing operating-contract concept: {token}")

    current = (ROOT / "docs" / "CURRENT_STATE.md").read_text()
    for token in ("#12", "#13", "A0", "BOOTSTRAP"):
        if token not in current:
            errors.append(f"CURRENT_STATE.md missing {token}")

    handoff = (ROOT / "docs" / "handoffs" / "LATEST.md").read_text()
    if "Next exact action" not in handoff or "#15" not in handoff:
        errors.append("LATEST handoff must contain next exact action and point to #15 after bootstrap")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Bootstrap contract validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Bootstrap contract validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
