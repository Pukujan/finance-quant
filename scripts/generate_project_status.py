"""Generate/check deterministic project-status documentation from machine state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "contracts" / "project" / "project-state.json"
ASSURANCE_PATH = ROOT / "contracts" / "assurance" / "capability-assurance-v1.json"
README_PATH = ROOT / "README.md"
BEGIN = "<!-- BEGIN GENERATED PROJECT STATUS -->"
END = "<!-- END GENERATED PROJECT STATUS -->"


def load_state() -> tuple[dict, dict]:
    return json.loads(STATE_PATH.read_text(encoding="utf-8")), json.loads(ASSURANCE_PATH.read_text(encoding="utf-8"))


def render_block() -> str:
    state, assurance = load_state()
    phase = next(p for p in assurance["phases"] if p["id"] == state["assurance_phase"])
    return "\n".join(
        [
            BEGIN,
            "## Project status (generated)",
            "",
            f"- Architecture: `{state['architecture']}`",
            f"- Status: **{state['status']}**",
            f"- Active epic / issue: **#{state['active_epic']} / #{state['active_issue']}**",
            f"- Assurance phase: **{phase['id']} — {phase['name']}**",
            f"- Current capability: **{state['current_capability']}**",
            f"- Trading authority: **{state['authority']['trading']}**",
            f"- Paper trading enabled: **{str(state['authority']['paper_trading_enabled']).lower()}**",
            f"- Live capital enabled: **{str(state['authority']['live_capital_enabled']).lower()}**",
            f"- Frontend authority: **{state['authority']['frontend']}**",
            f"- Legacy Phase B: **{state['legacy_phase_b']['status']}** (evidence preserved)",
            f"- Next planned issue after bootstrap: **#{state['next_issue']}**",
            "",
            "Machine source: `contracts/project/project-state.json`; assurance source: `contracts/assurance/capability-assurance-v1.json`.",
            END,
        ]
    )


def _extract_block(text: str) -> str:
    if BEGIN not in text or END not in text:
        raise ValueError("README is missing generated project-status markers")
    start = text.index(BEGIN)
    end = text.index(END, start) + len(END)
    return text[start:end]


def _normalized_lines(text: str) -> list[str]:
    """Compare semantic generated content independent of checkout line endings."""
    return text.replace("\r\n", "\n").replace("\r", "\n").splitlines()


def replace_block(text: str, block: str) -> str:
    if BEGIN not in text or END not in text:
        raise ValueError("README is missing generated project-status markers")
    prefix, rest = text.split(BEGIN, 1)
    _, suffix = rest.split(END, 1)
    return prefix.rstrip() + "\n\n" + block + suffix


def expected_readme() -> str:
    return replace_block(README_PATH.read_text(encoding="utf-8"), render_block())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    current = README_PATH.read_text(encoding="utf-8")
    expected_block = render_block()
    if args.check:
        current_block = _extract_block(current)
        if _normalized_lines(current_block) != _normalized_lines(expected_block):
            print("README generated project status is stale; run: python scripts/generate_project_status.py --write")
            return 1
        print("Generated project status: PASS")
        return 0

    README_PATH.write_text(replace_block(current, expected_block), encoding="utf-8", newline="\n")
    print("Updated README generated project status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
