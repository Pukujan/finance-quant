import pytest

from finance_quant.experiments.ledger import RunSpec
from finance_quant.experiments.rerun import rerun_receipt, rerun_runbook
from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore, pit_depth_ok


def test_fresh_environment_rerun_reproduces_run_id_and_metrics(tmp_path):
    spec = RunSpec("B1", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    receipt = rerun_receipt(spec, {"ic": 0.2}, {"model": "abc"},
                            tmp_path / "a.db", tmp_path / "b.db", tmp_path / "export")
    assert receipt["same_run_id"]
    assert receipt["same_metrics"]
    assert receipt["same_spec_hash"]


def test_rerun_with_pit_depth_gate_succeeds_on_fixture(tmp_path):
    store = MemoryGoldStore()
    for rec in generate():
        store.put(rec)
    ok, msg = pit_depth_ok(store)
    assert ok, msg
    spec = RunSpec("B1", "c" * 40, "env", store.snapshot_pin(), "ir", "model", (1,), "split", "cost")
    receipt = rerun_receipt(spec, {"ic": 0.2}, {"model": "abc"},
                            tmp_path / "a.db", tmp_path / "b.db", tmp_path / "export",
                            pit_store=store)
    assert receipt["same_run_id"]


def test_rerun_with_pit_depth_gate_fails_on_shallow_store(tmp_path):
    store = MemoryGoldStore()
    # Only two instruments and no universe namespace => fails depth gate.
    store.put(type("R", (), {
        "namespace": "bar", "instrument_id": "A", "vt": "2024-01-02", "kt": "2024-01-02",
        "payload": {}, "source": "x", "revision": 0, "key": lambda self: ("bar", "A", "2024-01-02"),
        "canonical": lambda self: b"a",
    })())
    store.put(type("R", (), {
        "namespace": "bar", "instrument_id": "B", "vt": "2024-01-02", "kt": "2024-01-02",
        "payload": {}, "source": "x", "revision": 0, "key": lambda self: ("bar", "B", "2024-01-02"),
        "canonical": lambda self: b"b",
    })())
    ok, msg = pit_depth_ok(store, min_instruments=4, min_bars=2, min_namespaces={"bar"})
    assert not ok
    assert "instruments" in msg


def test_pit_depth_gate_catches_future_dated_kt(tmp_path):
    store = MemoryGoldStore()
    store.put(type("R", (), {
        "namespace": "bar", "instrument_id": "A", "vt": "2024-01-02", "kt": "2024-01-01",
        "payload": {}, "source": "x", "revision": 0, "key": lambda self: ("bar", "A", "2024-01-02"),
        "canonical": lambda self: b"a",
    })())
    store.put(type("R", (), {
        "namespace": "universe", "instrument_id": "A", "vt": "2024-01-02", "kt": "2024-01-02",
        "payload": {}, "source": "x", "revision": 0, "key": lambda self: ("universe", "A", "2024-01-02"),
        "canonical": lambda self: b"b",
    })())
    ok, msg = pit_depth_ok(store, min_instruments=1, min_bars=1)
    assert not ok
    assert "kt < vt" in msg


def test_runbook_is_nonempty():
    assert "Fresh-environment rerun runbook" in rerun_runbook()
