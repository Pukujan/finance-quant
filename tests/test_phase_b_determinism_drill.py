"""Tests for run_phase_b_determinism_drill with monkeypatched sub-runners."""
from __future__ import annotations

import json
from pathlib import Path

import scripts.run_b1_b5_phase_b as b1b5_module
import scripts.run_lean_phase_b as lean_module
import scripts.run_qlib_phase_b as qlib_module
import scripts.run_phase_b_determinism_drill as drill
from scripts.run_phase_b_determinism_drill import (
    content_hash,
    hashes_match,
    run_b1_b5_receipt_hash,
    run_fixture_hash,
    run_lean_receipt_hash,
    run_qlib_receipt_hash,
    run_one_iteration,
    main,
    run_benchmark,
)


def test_content_hash_deterministic():
    assert content_hash({"a": 1}) == content_hash({"a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_hashes_match_all_same():
    fake = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1", "r2": "b2"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    ok, mismatches = hashes_match([fake, fake.copy(), fake.copy()])
    assert ok is True
    assert mismatches == []


def test_hashes_match_fixture_differs():
    a = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    b = dict(a, fixture_hash="bbb")
    ok, mismatches = hashes_match([a, b])
    assert ok is False
    assert any("fixture_hash" in m for m in mismatches)


def test_hashes_match_b1b5_key_differs():
    a = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    b = dict(a, b1_b5_receipts={"r1": "b1", "r2": "b2"})
    ok, mismatches = hashes_match([a, b])
    assert ok is False
    assert any("b1_b5_receipts keys differ" in m for m in mismatches)


def test_hashes_match_b1b5_value_differs():
    a = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    b = dict(a, b1_b5_receipts={"r1": "b1_changed"})
    ok, mismatches = hashes_match([a, b])
    assert ok is False
    assert any("b1_b5_receipts" in m and "mismatch" in m for m in mismatches)


def test_hashes_match_qlib_differs():
    a = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    b = dict(a, qlib_receipt="rrr")
    ok, mismatches = hashes_match([a, b])
    assert ok is False
    assert any("qlib_receipt" in m for m in mismatches)


def test_hashes_match_lean_differs():
    a = {
        "run_index": 0,
        "fixture_hash": "aaa",
        "b1_b5_receipts": {"r1": "b1"},
        "qlib_receipt": "qqq",
        "lean_receipt": "lll",
    }
    b = dict(a, lean_receipt="mmm")
    ok, mismatches = hashes_match([a, b])
    assert ok is False
    assert any("lean_receipt" in m for m in mismatches)


def test_run_fixture_hash_default():
    h = run_fixture_hash(Path("nonexistent_fixture_dir_xyz"))
    assert isinstance(h, str)
    assert len(h) == 64


def test_run_fixture_hash_from_manifest(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest = {"records": [{"a": 1}]}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    h = run_fixture_hash(tmp_path)
    assert isinstance(h, str)
    assert len(h) == 64


def test_run_b1_b5_receipt_hash(tmp_path, monkeypatch):
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    monkeypatch.setattr(b1b5_module, "main", lambda: 0)
    receipt_path = work_dir / "experiment_ledger_receipts.jsonl"
    receipt_path.write_text(
        json.dumps({"run_id": "abc", "receipt_type": "ExperimentLedger"}) + "\n"
    )
    (work_dir / "b1_b5_rank_ic.json").write_text("{}")
    result = run_b1_b5_receipt_hash(tmp_path, work_dir)
    assert "abc" in result


def test_run_qlib_receipt_hash(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    work_dir = tmp_path / "work"
    out_dir = work_dir / "qlib_out"
    out_dir.mkdir(parents=True)
    mlflow_path = out_dir / "mlflow_run.json"
    mlflow_path.write_text(json.dumps({"run_id": "qlib-1", "status": "SUCCESS"}) + "\n")

    def fake_main(argv):
        return 0

    monkeypatch.setattr(qlib_module, "main", fake_main)
    result = run_qlib_receipt_hash(fixture_dir, work_dir)
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_lean_receipt_hash(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    out_path = work_dir / "lean_receipt.json"
    out_path.write_text(json.dumps({"strategy_id": "test", "status": "success"}) + "\n")

    def fake_main(argv):
        return 0

    monkeypatch.setattr(lean_module, "main", fake_main)
    result = run_lean_receipt_hash(fixture_dir, work_dir)
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_one_iteration(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    work_dir = tmp_path / "work"
    b1b5_dir = work_dir / "b1b5_0"
    b1b5_dir.mkdir(parents=True)
    qlib_dir = work_dir / "qlib_0" / "qlib_out"
    qlib_dir.mkdir(parents=True)
    lean_dir = work_dir / "lean_0"
    lean_dir.mkdir(parents=True)

    (b1b5_dir / "experiment_ledger_receipts.jsonl").write_text(
        json.dumps({"run_id": "abc", "receipt_type": "ExperimentLedger"}) + "\n"
    )
    (qlib_dir / "mlflow_run.json").write_text(
        json.dumps({"run_id": "qlib-1", "status": "SUCCESS"}) + "\n"
    )
    (lean_dir / "lean_receipt.json").write_text(
        json.dumps({"strategy_id": "test", "status": "success"}) + "\n"
    )

    monkeypatch.setattr(b1b5_module, "main", lambda: 0)
    monkeypatch.setattr(qlib_module, "main", lambda argv: 0)
    monkeypatch.setattr(lean_module, "main", lambda argv: 0)

    result = run_one_iteration(0, fixture_dir, work_dir)
    assert result["run_index"] == 0
    assert "fixture_hash" in result
    assert "b1_b5_receipts" in result
    assert "qlib_receipt" in result
    assert "lean_receipt" in result


def test_main_returns_zero_on_match(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    counter = {"n": 0}

    def fake_benchmark(n_runs, fixture_dir=None):
        counter["n"] += 1
        fake_result = {
            "fixture_hash": "hash_" + str(counter["n"]),
            "b1_b5_receipts": {"abc": "receipt_hash"},
            "qlib_receipt": "qlib_hash",
            "lean_receipt": "lean_hash",
        }
        results = [dict(fake_result, run_index=i) for i in range(n_runs)]
        return True, results, []

    monkeypatch.setattr(drill, "run_benchmark", fake_benchmark)
    code = main(["--runs", "2", "--fixture-dir", str(fixture_dir)])
    assert code == 0
    assert counter["n"] == 1


def test_main_returns_one_on_mismatch(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()

    def fake_benchmark(n_runs, fixture_dir=None):
        results = [
            {
                "run_index": 0,
                "fixture_hash": "aaa",
                "b1_b5_receipts": {"abc": "h1"},
                "qlib_receipt": "q1",
                "lean_receipt": "l1",
            },
            {
                "run_index": 1,
                "fixture_hash": "bbb",
                "b1_b5_receipts": {"abc": "h2"},
                "qlib_receipt": "q2",
                "lean_receipt": "l2",
            },
        ]
        return False, results, ["fixture_hash mismatch"]

    monkeypatch.setattr(drill, "run_benchmark", fake_benchmark)
    code = main(["--runs", "2", "--fixture-dir", str(fixture_dir)])
    assert code == 1


def test_run_benchmark_calls_runners(tmp_path, monkeypatch):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    calls = {"b1b5": 0, "qlib": 0, "lean": 0, "fixture": 0}

    def fake_fixture_hash(fixture_dir):
        calls["fixture"] += 1
        return "fixture_hash_0"

    def fake_b1b5(fixture_dir, work_dir):
        calls["b1b5"] += 1
        return {"abc": "receipt_hash_0"}

    def fake_qlib(fixture_dir, work_dir):
        calls["qlib"] += 1
        return "qlib_hash_0"

    def fake_lean(fixture_dir, work_dir):
        calls["lean"] += 1
        return "lean_hash_0"

    monkeypatch.setattr(drill, "run_fixture_hash", fake_fixture_hash)
    monkeypatch.setattr(drill, "run_b1_b5_receipt_hash", fake_b1b5)
    monkeypatch.setattr(drill, "run_qlib_receipt_hash", fake_qlib)
    monkeypatch.setattr(drill, "run_lean_receipt_hash", fake_lean)

    all_match, results, mismatches = run_benchmark(n_runs=2, fixture_dir=fixture_dir)
    assert all_match is True
    assert len(results) == 2
    assert mismatches == []
    assert calls["fixture"] == 2
    assert calls["b1b5"] == 2
    assert calls["qlib"] == 2
    assert calls["lean"] == 2
