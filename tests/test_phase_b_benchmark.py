import json

from scripts import run_phase_b_benchmark as benchmark


def test_run_benchmark_consolidates_receipt_hashes(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    report_path = tmp_path / "reports" / "phase_b_benchmark.json"
    monkeypatch.setattr(
        benchmark,
        "_freeze_or_load",
        lambda path, freeze: ({"manifest_id": "phase-b-fixture-v0"}, "fixture-hash"),
    )
    monkeypatch.setattr(
        benchmark,
        "_run_b1_b5",
        lambda path: ({"runs": [{"experiment_id": "B1-sma3"}]}, ["b1-hash"]),
    )
    monkeypatch.setattr(benchmark, "_run_qlib", lambda manifest, path: ({"status": "SUCCESS"}, "qlib-hash"))
    monkeypatch.setattr(benchmark, "_run_lean", lambda report, path: ({"status": "success"}, "lean-hash"))

    result = benchmark.run_benchmark(fixture_dir, report_path)

    assert result["status"] == "success"
    assert result["receipt_hashes"] == {
        "fixture_manifest": "fixture-hash",
        "b1_b5": ["b1-hash"],
        "qlib": "qlib-hash",
        "lean": "lean-hash",
    }
    assert json.loads(report_path.read_text())["qlib"]["status"] == "SUCCESS"


def test_main_passes_freeze_and_report_arguments(tmp_path, monkeypatch):
    report_path = tmp_path / "result.json"
    seen = {}

    def fake_run(fixture_dir, report, freeze):
        seen.update(fixture_dir=fixture_dir, report=report, freeze=freeze)
        return {"status": "success"}

    monkeypatch.setattr(benchmark, "run_benchmark", fake_run)
    assert benchmark.main(["--fixture-dir", str(tmp_path / "fixture"), "--report", str(report_path), "--freeze"]) == 0
    assert seen == {"fixture_dir": tmp_path / "fixture", "report": report_path, "freeze": True}
