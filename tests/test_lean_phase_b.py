import json
from pathlib import Path

from scripts.run_lean_phase_b import (
    MODELS,
    _hash,
    _load_signals,
    build_custom_data_source,
    detect_lean_cli,
    main,
    run_variant,
)


def test_models_named():
    assert MODELS["fill"] == "ImmediateSameBarFillModel"
    assert MODELS["slippage"] == "ConstantSlippageModel"
    assert MODELS["fee"] == "ZeroFeeModel"


def test_load_signals_default():
    signals = _load_signals(None)
    assert set(signals.keys()) == {"B1", "B2", "B3", "B4", "B5"}


def test_load_signals_from_file(tmp_path):
    path = tmp_path / "signals.json"
    path.write_text(json.dumps({"signals": {"B1": [1, 2], "B2": [3]}}))
    signals = _load_signals(path)
    assert signals["B1"] == [1, 2]
    assert signals["B2"] == [3]
    assert signals["B3"] == []


def test_build_custom_data_source():
    signals = {"B1": [1]}
    src = build_custom_data_source(signals)
    assert "PhaseBSignalData" in src
    assert "B1" in src


def test_hash_deterministic():
    assert _hash({"a": 1}) == _hash({"a": 1})


def test_detect_lean_cli_from_config(tmp_path):
    executable = tmp_path / "lean.exe"
    executable.write_text("stub")
    (tmp_path / "lean.json").write_text(json.dumps({"executable": "lean.exe"}))
    assert detect_lean_cli(tmp_path) == str(executable)


def test_detect_lean_cli_from_path(tmp_path, monkeypatch):
    (tmp_path / "lean.json").write_text("{}")
    monkeypatch.setattr("scripts.run_lean_phase_b.shutil.which", lambda name: "/bin/lean")
    assert detect_lean_cli(tmp_path) == "/bin/lean"


def test_main_runs_detected_lean_cli(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs["cwd"]))
        assert (kwargs["cwd"] / "PhaseBSignalData.py").exists()
        return type("Completed", (), {"returncode": 0, "stdout": "{}", "stderr": ""})()

    monkeypatch.setattr("scripts.run_lean_phase_b.detect_lean_cli", lambda: "lean")
    monkeypatch.setattr("scripts.run_lean_phase_b.subprocess.run", fake_run)
    out = tmp_path / "receipt.json"
    assert main(["--out", str(out)]) == 0
    assert [command[0][1] for command in calls] == ["backtest", "backtest"]
    assert json.loads(out.read_text())["engine"] == "lean-cli"


def test_run_variant():
    signals = {"B1": [1, 2], "B2": [3]}
    result = run_variant(signals, 5.0, 5.0)
    assert result["variant"] == "nominal"
    assert result["models"] == MODELS
    assert result["signal_count"] == 3


def test_main_uses_stub_when_lean_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.run_lean_phase_b.detect_lean_cli", lambda: None)
    out = tmp_path / "receipt.json"
    assert main(["--out", str(out)]) == 0
    receipt = json.loads(out.read_text())
    assert receipt["engine"] == "lean-subprocess-stub"


def test_main_nominal_and_stress(tmp_path):
    out = tmp_path / "receipt.json"
    signals = tmp_path / "signals.json"
    signals.write_text(json.dumps({"signals": {"B1": [1]}}))
    code = main(["--signals", str(signals), "--out", str(out)])
    assert code == 0
    receipt = json.loads(out.read_text())
    assert receipt["cost_stress"]["nominal"]["variant"] == "nominal"
    assert receipt["cost_stress"]["2x_slippage"]["variant"] == "2x_slippage"
    assert out.with_name(out.stem + "_custom_data.py").exists()
