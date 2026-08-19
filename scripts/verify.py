"""Run full verification: pytest then smoke.py."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pytest and smoke runner")
    parser.add_argument("--pytest-args", default="-q", help="extra args for pytest")
    parser.add_argument("--smoke-script", default=str(ROOT / "scripts" / "smoke.py"),
                        help="path to smoke runner")
    args = parser.parse_args(argv)

    pytest = subprocess.run([sys.executable, "-m", "pytest", "tests"] + args.pytest_args.split(), cwd=ROOT)
    if pytest.returncode != 0:
        return pytest.returncode
    smoke = subprocess.run([sys.executable, args.smoke_script], cwd=ROOT)
    return smoke.returncode


if __name__ == "__main__":
    raise SystemExit(main())
