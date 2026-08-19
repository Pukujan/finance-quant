"""Overnight smoke: PIT bake-off, B1-B5, search batch. Exit 0 only if all pass."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/run_pit_bakeoff.py",
    "scripts/run_b1_b5_campaign.py",
    "scripts/run_search_batch.py",
    "scripts/run_search_scorecard.py",
    "scripts/run_rank_ic_report.py",
    "scripts/run_two_stage.py",
    "scripts/alpha158_coverage.py",
]


def main() -> int:
    py = sys.executable
    pytest = subprocess.run([py, "-m", "pytest", "tests", "-q"], cwd=ROOT)
    if pytest.returncode != 0:
        print("FAIL pytest", file=sys.stderr)
        return pytest.returncode
    print("OK pytest")
    for rel in SCRIPTS:
        proc = subprocess.run([py, str(ROOT / rel)], cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"FAIL {rel}", file=sys.stderr)
            print(proc.stderr[-500:] if proc.stderr else "", file=sys.stderr)
            return proc.returncode
        print(f"OK {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
