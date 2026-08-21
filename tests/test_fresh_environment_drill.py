"""Tests for scripts/run_fresh_environment_drill.py.

All subprocess calls are monkeypatched so the test suite does NOT actually
create venvs, install packages, or run the full drill.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_fresh_environment_drill import drill, main  # noqa: E402


def _make_ok(returncode=0):
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.returncode = returncode
    r.stdout = ""
    r.stderr = ""
    return r


@pytest.fixture
def fake_repo(tmp_path):
    (tmp_path / "requirements-dev.txt").write_text("pytest>=8\n")
    (tmp_path / "finance_quant").mkdir()
    (tmp_path / "finance_quant" / "__init__.py").write_text("")
    (tmp_path / "finance_quant" / "__main__.py").write_text(
        'import sys; sys.exit(0)'
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "__init__.py").write_text("")
    (tmp_path / "tests" / "conftest.py").write_text("")
    return tmp_path


def _patch_all():
    """Return a dict of patches that replace every subprocess call."""
    return {
        "subprocess.run": MagicMock(return_value=_make_ok()),
    }


class TestDrillLogic:
    def test_all_pass_returns_success(self, fake_repo):
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=_make_ok()):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        result = drill(repo=fake_repo)

        assert result["success"] is True
        assert result["pytest_ok"] is True
        assert result["verify_ok"] is True

    def test_pytest_fail_marks_failure(self, fake_repo):
        fail_r = _make_ok(returncode=1)
        fail_r.stdout = "FAILED test_foo.py::test_bar"
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=fail_r):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        result = drill(repo=fake_repo)

        assert result["success"] is False
        assert result["pytest_ok"] is False
        assert "FAILED" in result["pytest_output"]

    def test_verify_fail_marks_failure(self, fake_repo):
        fail_r = _make_ok(returncode=2)
        fail_r.stderr = "verify failed"
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=_make_ok()):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=fail_r):
                        result = drill(repo=fake_repo)

        assert result["success"] is False
        assert result["verify_ok"] is False

    def test_install_fail_returns_early(self, fake_repo):
        fail_r = _make_ok(returncode=1)
        fail_r.stderr = "pip install error"
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=fail_r):
                with patch("scripts.run_fresh_environment_drill._run_tests") as mock_tests:
                    with patch("scripts.run_fresh_environment_drill._run_verify") as mock_verify:
                        result = drill(repo=fake_repo)

        assert result["success"] is False
        assert result["pytest_ok"] is False
        assert "pip install error" in result["pytest_output"]
        mock_tests.assert_not_called()
        mock_verify.assert_not_called()

    def test_exception_caught(self, fake_repo):
        with patch("scripts.run_fresh_environment_drill._create_venv", side_effect=RuntimeError("boom")):
            result = drill(repo=fake_repo)

        assert result["success"] is False
        assert "boom" in result["pytest_output"]

    def test_keep_venv_on_failure_leaves_dir(self, fake_repo):
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                fail_r = _make_ok(returncode=1)
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=fail_r):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        result = drill(repo=fake_repo, keep_venv_on_failure=True)

        # venv_dir should still exist because we asked to keep it
        assert result["venv_dir"].exists()
        # Clean up for test hygiene
        import shutil
        shutil.rmtree(result["venv_dir"], ignore_errors=True)

    def test_cleanup_on_success(self, fake_repo):
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=_make_ok()):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        result = drill(repo=fake_repo)

        # venv should have been removed
        assert not result["venv_dir"].exists()
        assert result["success"] is True


class TestMain:
    def test_main_returns_zero_on_success(self, fake_repo):
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=_make_ok()):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        code = main(argv=["--repo-path", str(fake_repo)])

        assert code == 0

    def test_main_returns_nonzero_on_failure(self, fake_repo):
        fail_r = _make_ok(returncode=1)
        with patch("scripts.run_fresh_environment_drill._create_venv"):
            with patch("scripts.run_fresh_environment_drill._install_deps", return_value=_make_ok()):
                with patch("scripts.run_fresh_environment_drill._run_tests", return_value=fail_r):
                    with patch("scripts.run_fresh_environment_drill._run_verify", return_value=_make_ok()):
                        code = main(argv=["--repo-path", str(fake_repo)])

        assert code == 1

    def test_main_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(argv=["--help"])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "--keep-venv-on-failure" in captured.out
        assert "--repo-path" in captured.out
