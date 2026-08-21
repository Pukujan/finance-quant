"""Tests for scripts/run_docker_clean_runner_drill.py that do NOT require Docker.

All subprocess calls are monkeypatched so the logic can be verified offline.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
MODULE = "scripts.run_docker_clean_runner_drill"


def _import():
    import importlib
    import sys
    mod = importlib.import_module(MODULE)
    return mod


@pytest.fixture(autouse=True)
def clear_cached_module():
    yield
    import sys
    sys.modules.pop(MODULE, None)


# -- docker_available --

class TestDockerAvailable:
    def test_returns_true_when_docker_info_succeeds(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["docker", "info"], returncode=0, stdout="", stderr=""
            )
            assert mod.docker_available() is True

    def test_returns_false_when_docker_not_found(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run", side_effect=FileNotFoundError):
            assert mod.docker_available() is False

    def test_returns_false_on_timeout(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="docker info", timeout=15)):
            assert mod.docker_available() is False

    def test_returns_false_on_nonzero_rc(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["docker", "info"], returncode=1, stdout="", stderr="error"
            )
            assert mod.docker_available() is False


# -- generate_dockerfile --

class TestGenerateDockerfile:
    def test_from_template(self, tmp_path):
        mod = _import()
        tpl = tmp_path / "Dockerfile.drill.template"
        tpl.write_text("FROM custom:latest\n")
        content = mod.generate_dockerfile(tpl)
        assert "FROM custom:latest" in content

    def test_inline_fallback_when_no_template(self):
        mod = _import()
        content = mod.generate_dockerfile(template=None)
        assert "FROM python:3.11-slim" in content
        assert "CMD" in content

    def test_inline_fallback_when_template_missing(self):
        mod = _import()
        content = mod.generate_dockerfile(template=Path("/nonexistent/template"))
        assert "FROM python:3.11-slim" in content


# -- prepare_build_context --

class TestPrepareBuildContext:
    def test_copies_required_files(self, tmp_path):
        mod = _import()
        src_root = tmp_path / "src"
        build_dir = tmp_path / "build"
        src_root.mkdir()
        build_dir.mkdir()
        (src_root / "requirements-dev.txt").write_text("pytest\n")
        (src_root / "pyproject.toml").write_text("")
        (src_root / "finance_quant").mkdir()
        (src_root / "finance_quant" / "__init__.py").write_text("")
        (src_root / "scripts").mkdir()
        (src_root / "tests").mkdir()

        with patch.object(mod, "ROOT", src_root):
            dockerfile = mod.prepare_build_context("FROM test\n", build_dir)

        assert dockerfile.exists()
        assert (build_dir / "requirements-dev.txt").exists()
        assert (build_dir / "pyproject.toml").exists()
        assert (build_dir / "finance_quant" / "__init__.py").exists()


# -- build_image --

class TestBuildImage:
    def test_calls_docker_build(self, tmp_path):
        mod = _import()
        (tmp_path / "Dockerfile.drill").write_text("FROM test\n")
        with patch(f"{MODULE}.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="built", stderr=""
            )
            mod.build_image(tmp_path, "test-tag")
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "docker" in call_args
            assert "build" in call_args
            assert "test-tag" in call_args


# -- run_container --

class TestRunContainer:
    def test_calls_docker_run(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="ok", stderr=""
            )
            mod.run_container("test-tag", "test-container")
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "docker" in call_args
            assert "run" in call_args
            assert "test-container" in call_args


# -- cleanup --

class TestCleanup:
    def test_calls_rm_and_rmi(self):
        mod = _import()
        with patch(f"{MODULE}.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
            mod.cleanup("test-tag", "test-container")
            assert mock_run.call_count == 2
            first_call = mock_run.call_args_list[0][0][0]
            assert "rm" in first_call
            second_call = mock_run.call_args_list[1][0][0]
            assert "rmi" in second_call


# -- run_drill (integration with mocks) --

class TestRunDrill:
    def test_skips_when_docker_unavailable(self, capsys):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=False):
            rc = mod.run_drill()
        assert rc == 0
        captured = capsys.readouterr()
        assert "SKIP" in captured.out

    def test_build_failure_returns_1(self, capsys):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=True):
            with patch(f"{MODULE}.build_image") as mock_build:
                mock_build.return_value = subprocess.CompletedProcess(
                    args=[], returncode=1, stdout="", stderr="build error"
                )
                with patch(f"{MODULE}.cleanup"):
                    rc = mod.run_drill()
        assert rc == 1
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_container_success_returns_0(self, capsys):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=True):
            with patch(f"{MODULE}.build_image") as mock_build:
                mock_build.return_value = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout="ok", stderr=""
                )
                with patch(f"{MODULE}.run_container") as mock_run:
                    mock_run.return_value = subprocess.CompletedProcess(
                        args=[], returncode=0, stdout="PASS output", stderr=""
                    )
                    with patch(f"{MODULE}.cleanup"):
                        rc = mod.run_drill()
        assert rc == 0
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_container_failure_returns_1(self, capsys):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=True):
            with patch(f"{MODULE}.build_image") as mock_build:
                mock_build.return_value = subprocess.CompletedProcess(
                    args=[], returncode=0, stdout="ok", stderr=""
                )
                with patch(f"{MODULE}.run_container") as mock_run:
                    mock_run.return_value = subprocess.CompletedProcess(
                        args=[], returncode=1, stdout="", stderr="container error"
                    )
                    with patch(f"{MODULE}.cleanup"):
                        rc = mod.run_drill()
        assert rc == 1
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_keep_flag_printed_on_failure(self, capsys):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=True):
            with patch(f"{MODULE}.build_image") as mock_build:
                mock_build.return_value = subprocess.CompletedProcess(
                    args=[], returncode=1, stdout="", stderr="fail"
                )
                rc = mod.run_drill(keep=True)
        assert rc == 1
        captured = capsys.readouterr()
        assert "--keep" in captured.out


# -- main CLI --

class TestMain:
    def test_main_returns_0_on_skip(self):
        mod = _import()
        with patch(f"{MODULE}.docker_available", return_value=False):
            assert mod.main([]) == 0

    def test_main_passes_keep_flag(self):
        mod = _import()
        with patch(f"{MODULE}.run_drill") as mock_drill:
            mock_drill.return_value = 0
            mod.main(["--keep"])
            mock_drill.assert_called_once()
            assert mock_drill.call_args.kwargs["keep"] is True

    def test_main_passes_template_flag(self, tmp_path):
        mod = _import()
        tpl = tmp_path / "Dockerfile.drill.template"
        tpl.write_text("FROM test\n")
        with patch(f"{MODULE}.run_drill") as mock_drill:
            mock_drill.return_value = 0
            mod.main(["--template", str(tpl)])
            mock_drill.assert_called_once()
            assert mock_drill.call_args.kwargs["template"] == tpl

    def test_main_help(self, capsys):
        mod = _import()
        with pytest.raises(SystemExit) as exc:
            mod.main(["--help"])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "--keep" in captured.out
