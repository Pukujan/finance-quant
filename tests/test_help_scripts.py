"""Tests for --help on scripts that had no argparse CLI."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/run_b1_b5_campaign.py",
    "scripts/run_search_batch.py",
    "scripts/run_search_scorecard.py",
    "scripts/run_two_stage.py",
]


def _run(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    script = ROOT / script_name
    return subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_help_b1_b5_campaign():
    result = _run("scripts/run_b1_b5_campaign.py", ["--help"])
    assert result.returncode == 0
    assert "B1-B5" in result.stdout or "baselines" in result.stdout


def test_help_run_search_batch():
    result = _run("scripts/run_search_batch.py", ["--help"])
    assert result.returncode == 0
    assert "RANDOM" in result.stdout or "GP" in result.stdout


def test_help_run_search_scorecard():
    result = _run("scripts/run_search_scorecard.py", ["--help"])
    assert result.returncode == 0
    assert "scorecard" in result.stdout.lower() or "bake-off" in result.stdout.lower()


def test_help_run_two_stage():
    result = _run("scripts/run_two_stage.py", ["--help"])
    assert result.returncode == 0
    assert "two-stage" in result.stdout.lower() or "feature_eval" in result.stdout


def test_default_run_two_stage():
    """Ensure default (no-arg) behavior still works."""
    result = _run("scripts/run_two_stage.py", [])
    assert result.returncode == 0
