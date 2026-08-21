import json

from scripts import run_cost_stress_report as report


def test_compare_runs_both_costs_and_checks_monotonicity(monkeypatch):
    calls = []

    def fake_runner(signals, slippage, default):
        calls.append(slippage)
        return {"strategies": {name: {"gross_return": 0.10, "turnover": 10.0,
                                      "returns": [0.01, -0.01]} for name in report.STRATEGIES}}

    monkeypatch.setattr(report.run_lean_phase_b, "run_variant", fake_runner)
    result = report.compare({name: [{}] for name in report.STRATEGIES})
    assert calls == [5.0, 10.0]
    assert result["monotonic_degradation_ok"] is True
    assert result["cost_models"]["2x_slippage"]["aggregate"]["total_return"] < result["cost_models"]["nominal"]["aggregate"]["total_return"]


def test_compare_reports_failure_when_runner_metrics_improve(monkeypatch):
    def fake_runner(signals, slippage, default):
        return {"strategies": {"B1": {"total_return": 0.20 if slippage > 5 else 0.10,
                                       "turnover": 1.0, "returns": [0.1]}, **{
            name: {} for name in report.STRATEGIES if name != "B1"}}}

    monkeypatch.setattr(report.run_lean_phase_b, "run_variant", fake_runner)
    assert report.compare({name: [] for name in report.STRATEGIES})["monotonic_degradation_ok"] is False


def test_main_writes_report_and_exit_code(tmp_path, monkeypatch):
    signals = tmp_path / "signals.json"
    out = tmp_path / "reports" / "cost_stress.json"
    signals.write_text(json.dumps({"signals": {"B1": [1]}}))
    monkeypatch.setattr(report.run_lean_phase_b, "run_variant", lambda signals, slippage, default: {})
    assert report.main(["--signals", str(signals), "--out", str(out)]) == 0
    assert json.loads(out.read_text())["monotonic_degradation_ok"] is True
