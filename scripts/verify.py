"""Run full verification: pytest then smoke.py, with optional Phase B fixture run."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHASE_B_FIXTURE_DIR = ROOT / "data" / "fixtures" / "phase-b"
PHASE_B_REPORT_PATH = ROOT / "reports" / "b1_b5_rank_ic.json"
EXPECTED_PHASE_B_EXPERIMENTS = {"B1-sma3", "B2-walk-forward", "B3-momentum", "B4-xs-rank", "B5-buy-hold"}


def run_phase_b() -> int:
    """Run B1-B5 on the canonical fixture and verify the report."""
    from scripts import run_b1_b5_phase_b

    result = run_b1_b5_phase_b.main()
    if result != 0:
        return result

    if not PHASE_B_REPORT_PATH.exists():
        print("error: phase-b report not found", file=sys.stderr)
        return 1

    report = json.loads(PHASE_B_REPORT_PATH.read_text(encoding="utf-8"))
    experiment_ids = {r["experiment_id"] for r in report.get("runs", [])}
    missing = EXPECTED_PHASE_B_EXPERIMENTS - experiment_ids
    if missing:
        print(f"error: missing phase-b experiments: {sorted(missing)}", file=sys.stderr)
        return 1
    print(f"phase-b verified: all {len(EXPECTED_PHASE_B_EXPERIMENTS)} experiments present")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pytest and smoke runner")
    parser.add_argument("--pytest-args", default="-q", help="extra args for pytest")
    parser.add_argument("--smoke-script", default=str(ROOT / "scripts" / "smoke.py"),
                        help="path to smoke runner")
    parser.add_argument("--phase-b", action="store_true", dest="phase_b",
                        help="after pytest+smoke, also run B1-B5 on the canonical fixture")
    args = parser.parse_args(argv)

    pytest = subprocess.run([sys.executable, "-m", "pytest", "tests"] + args.pytest_args.split(), cwd=ROOT)
    if pytest.returncode != 0:
        return pytest.returncode
    smoke = subprocess.run([sys.executable, args.smoke_script], cwd=ROOT)
    if smoke.returncode != 0:
        return smoke.returncode

    if args.phase_b:
        return run_phase_b()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
