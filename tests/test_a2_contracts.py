from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_a2_contract_validator_passes():
    result = subprocess.run(
        [sys.executable, "scripts/validate_a2_contracts.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
