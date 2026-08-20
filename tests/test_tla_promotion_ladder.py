"""TLC smoke check for the sealed-holdout promotion lifecycle."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TLA_DIR = ROOT / "formal" / "tla"
SPEC = TLA_DIR / "PromotionLadder.tla"
CONFIG = TLA_DIR / "PromotionLadder.cfg"


def _tlc_command() -> list[str] | None:
    """Return an installed TLC invocation without downloading or installing tools."""
    if tlc := shutil.which("tlc"):
        return [tlc]

    jar = os.environ.get("TLA2TOOLS_JAR")
    if jar is None:
        for candidate in (ROOT / "tla2tools.jar", TLA_DIR / "tla2tools.jar"):
            if candidate.is_file():
                jar = str(candidate)
                break
    if jar and Path(jar).is_file() and shutil.which("java"):
        return [shutil.which("java") or "java", "-cp", jar, "tlc2.TLC"]
    return None


def test_promotion_ladder_tla_files_exist_and_are_nonempty():
    for path in (SPEC, CONFIG):
        assert path.is_file(), f"missing TLA+ artifact: {path.relative_to(ROOT)}"
        assert path.stat().st_size > 0, f"empty TLA+ artifact: {path.relative_to(ROOT)}"


def test_promotion_ladder_tlc_has_no_invariant_violations():
    command = _tlc_command()
    if command is None:
        pytest.skip("TLC check skipped: neither tlc nor TLA2TOOLS_JAR with Java is installed")

    result = subprocess.run(
        [*command, "-config", CONFIG.name, SPEC.name],
        cwd=TLA_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0, f"TLC failed:\n{output}"
    assert "No error has been found" in output, f"TLC did not report a clean run:\n{output}"
