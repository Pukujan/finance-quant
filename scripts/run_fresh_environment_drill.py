"""Run a full fresh-environment drill: create temp venv, install deps, run tests + verify.

Usage:
    python scripts/run_fresh_environment_drill.py
    python scripts/run_fresh_environment_drill.py --keep-venv-on-failure
    python scripts/run_fresh_environment_drill.py --repo-path /path/to/finance-quant
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run *cmd* in *cwd* and return the CompletedProcess."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _create_venv(venv_dir: Path) -> None:
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_pip(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def _install_deps(venv_dir: Path, repo: Path) -> subprocess.CompletedProcess:
    pip = _venv_pip(venv_dir)
    req = repo / "requirements-dev.txt"
    return _run([str(pip), "install", "-r", str(req)], cwd=repo)


def _run_tests(venv_dir: Path, repo: Path) -> subprocess.CompletedProcess:
    py = _venv_python(venv_dir)
    return _run([str(py), "-m", "pytest", "tests", "-q"], cwd=repo)


def _run_verify(venv_dir: Path, repo: Path) -> subprocess.CompletedProcess:
    py = _venv_python(venv_dir)
    return _run([str(py), "-m", "finance_quant", "verify"], cwd=repo)


def drill(
    repo: Path | None = None,
    keep_venv_on_failure: bool = False,
) -> dict:
    """Execute the full drill and return a result dict.

    Returns
    -------
    dict with keys: venv_dir (Path), pytest_ok (bool), verify_ok (bool),
    pytest_output (str), verify_output (str), success (bool)
    """
    if repo is None:
        repo = Path(__file__).resolve().parents[1]

    venv_dir = Path(tempfile.mkdtemp(prefix="fq_drill_venv_"))
    result: dict = {
        "venv_dir": venv_dir,
        "pytest_ok": False,
        "verify_ok": False,
        "pytest_output": "",
        "verify_output": "",
        "success": False,
    }

    try:
        _create_venv(venv_dir)

        install_r = _install_deps(venv_dir, repo)
        if install_r.returncode != 0:
            result["pytest_output"] = f"pip install failed:\n{install_r.stderr}"
            return result

        pytest_r = _run_tests(venv_dir, repo)
        result["pytest_ok"] = pytest_r.returncode == 0
        result["pytest_output"] = pytest_r.stdout + pytest_r.stderr

        verify_r = _run_verify(venv_dir, repo)
        result["verify_ok"] = verify_r.returncode == 0
        result["verify_output"] = verify_r.stdout + verify_r.stderr

        result["success"] = result["pytest_ok"] and result["verify_ok"]
        return result

    except Exception as exc:
        result["pytest_output"] = f"drill exception: {exc}"
        return result

    finally:
        if result["success"] or not keep_venv_on_failure:
            shutil.rmtree(venv_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fresh-environment drill: temp venv -> install -> pytest -> verify",
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=None,
        help="Root of the finance-quant repo (default: auto-detect)",
    )
    parser.add_argument(
        "--keep-venv-on-failure",
        action="store_true",
        default=False,
        help="Do not remove the temp venv if the drill fails",
    )
    args = parser.parse_args(argv)

    result = drill(repo=args.repo_path, keep_venv_on_failure=args.keep_venv_on_failure)

    print(f"venv: {result['venv_dir']}")
    print(f"pytest : {'PASS' if result['pytest_ok'] else 'FAIL'}")
    print(f"verify : {'PASS' if result['verify_ok'] else 'FAIL'}")

    if not result["pytest_ok"]:
        print("--- pytest output ---")
        print(result["pytest_output"])

    if not result["verify_ok"]:
        print("--- verify output ---")
        print(result["verify_output"])

    if result["success"]:
        print("Overall: PASS (venv cleaned up)")
        return 0
    else:
        print(f"Overall: FAIL (venv kept at {result['venv_dir']})")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
