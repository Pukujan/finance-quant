"""Tests for scripts/verify.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify.py"


class TestVerifyFlag:
    def test_phase_b_flag_parse(self):
        from scripts.verify import main
        from unittest import mock

        with mock.patch("scripts.verify.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
            with mock.patch("scripts.verify.run_phase_b", return_value=0) as mock_pb:
                rc = main(["--phase-b"])
                assert rc == 0
                mock_pb.assert_called_once()

    def test_without_phase_b_flag_does_not_run_phase_b(self):
        from scripts.verify import main
        from unittest import mock

        with mock.patch("scripts.verify.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
            with mock.patch("scripts.verify.run_phase_b") as mock_pb:
                rc = main([])
                assert rc == 0
                mock_pb.assert_not_called()


class TestRunPhaseB:
    def test_run_phase_b_success(self, tmp_path, monkeypatch):
        report = tmp_path / "b1_b5_rank_ic.json"
        runs = [
            {"experiment_id": "B1-sma3", "n_signals": 1, "rank_ic": 0.1},
            {"experiment_id": "B2-walk-forward", "n_signals": 2, "rank_ic": 0.2},
            {"experiment_id": "B3-momentum", "n_signals": 3, "rank_ic": 0.3},
            {"experiment_id": "B4-xs-rank", "n_signals": 4, "rank_ic": 0.4},
            {"experiment_id": "B5-buy-hold", "n_signals": 5, "rank_ic": 0.5},
        ]
        report.write_text(json.dumps({"runs": runs}))

        from scripts.verify import run_phase_b, PHASE_B_REPORT_PATH
        monkeypatch.setattr("scripts.verify.PHASE_B_REPORT_PATH", report)

        with pytest.MonkeyPatch().context() as m:
            m.setattr("scripts.run_b1_b5_phase_b.main", lambda: 0)
            m.setattr("scripts.verify.PHASE_B_REPORT_PATH", report)
            rc = run_phase_b()
            assert rc == 0

    def test_run_phase_b_missing_report(self):
        from scripts.verify import run_phase_b
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            fake_report = Path(td) / "nonexistent.json"
            with pytest.MonkeyPatch().context() as m:
                m.setattr("scripts.run_b1_b5_phase_b.main", lambda: 0)
                m.setattr("scripts.verify.PHASE_B_REPORT_PATH", fake_report)
                rc = run_phase_b()
                assert rc != 0

    def test_run_phase_b_missing_experiment(self, tmp_path):
        report = tmp_path / "b1_b5_rank_ic.json"
        runs = [
            {"experiment_id": "B1-sma3", "n_signals": 1, "rank_ic": 0.1},
        ]
        report.write_text(json.dumps({"runs": runs}))

        with pytest.MonkeyPatch().context() as m:
            m.setattr("scripts.run_b1_b5_phase_b.main", lambda: 0)
            m.setattr("scripts.verify.PHASE_B_REPORT_PATH", report)
            from scripts.verify import run_phase_b
            rc = run_phase_b()
            assert rc != 0


class TestVerifyPytestFailure:
    def test_pytest_failure_returns_nonzero(self):
        from scripts.verify import main
        from unittest import mock

        fail_result = subprocess.CompletedProcess([], 1)
        pass_result = subprocess.CompletedProcess([], 0)

        def fake_run(cmd, cwd=None):
            if len(cmd) > 2 and "pytest" in cmd[2]:
                return fail_result
            return pass_result

        with mock.patch("scripts.verify.subprocess.run", side_effect=fake_run):
            rc = main(["--phase-b"])
            assert rc == 1

    def test_smoke_failure_returns_nonzero(self):
        from scripts.verify import main
        from unittest import mock

        pass_result = subprocess.CompletedProcess([], 0)
        fail_result = subprocess.CompletedProcess([], 1)
        call_count = [0]

        def fake_run(cmd, cwd=None):
            call_count[0] += 1
            if len(cmd) > 2 and "pytest" in cmd[2]:
                return pass_result
            return fail_result

        with mock.patch("scripts.verify.subprocess.run", side_effect=fake_run):
            rc = main([])
            assert rc == 1
