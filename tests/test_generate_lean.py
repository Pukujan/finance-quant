"""Tests for scripts/generate_lean.py as a standalone script."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_lean.py"


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        cwd=cwd or ROOT,
    )


def test_generate_lean_help():
    """The script must not raise ModuleNotFoundError when invoked directly."""
    result = _run(["--help"])
    assert result.returncode == 0
    assert "strategy-id" in result.stdout


def test_generate_lean_check():
    result = _run(["--check"])
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_generate_lean_writes_file(tmp_path):
    out = tmp_path / "subdir" / "generated.py"
    result = _run(["--out", str(out), "--symbols", "SPY", "--strategy-id", "test-standalone"])
    assert result.returncode == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "GeneratedFinanceQuantAlgorithm(QCAlgorithm)" in text
    assert "SPY" in text


def test_generate_lean_check_custom_hashes():
    result = _run([
        "--check",
        "--dataset-hash", "a" * 64,
        "--signal-hash", "b" * 64,
        "--strategy-id", "hash-test",
    ])
    assert result.returncode == 0


def test_generate_lean_rejects_bad_hash():
    result = _run(["--check", "--dataset-hash", "not-a-hash"])
    assert result.returncode == 2
    assert "must be a 64-character hex string" in result.stderr
