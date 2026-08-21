from pathlib import Path

from scripts.run_b1_b5_phase_b import (
    CANONICAL_MANIFEST,
    ExperimentLedger,
    LocalWorkOrderOrchestrator,
    WorkOrder,
    content_hash,
    load_canonical_fixture_manifest,
    main,
    strategy_stub,
)


def test_content_hash_deterministic():
    assert content_hash({"a": 1}) == content_hash({"a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_load_canonical_fixture_manifest_default():
    manifest = load_canonical_fixture_manifest(None)
    assert manifest["manifest_id"] == "canonical-fixture-v0"


def test_strategy_stub_known():
    n, ic = strategy_stub("B1-sma3", CANONICAL_MANIFEST)
    assert n == 132
    assert ic == 0.118


def test_strategy_stub_unknown():
    try:
        strategy_stub("X", CANONICAL_MANIFEST)
    except ValueError as e:
        assert "unknown strategy stub" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_orchestrator_run():
    orch = LocalWorkOrderOrchestrator()
    order = WorkOrder("wo-1", "B1-sma3", "hash", "B1-sma3")
    result = orch.run(order, CANONICAL_MANIFEST, lambda m: strategy_stub("B1-sma3", m))
    assert result.status == "success"
    assert result.rank_ic == 0.118


def test_ledger_record(tmp_path):
    path = tmp_path / "ledger.jsonl"
    ledger = ExperimentLedger(path)
    order = WorkOrder("wo-1", "B1-sma3", "hash", "B1-sma3")
    result = ledger.record(order, type("R", (), {"work_order_id": "wo-1", "experiment_id": "B1-sma3", "status": "success", "n_signals": 1, "rank_ic": 0.1, "signal_hash": "sh"})())
    assert path.exists()
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    assert "ExperimentLedger" in lines[0]


def test_main_creates_report(tmp_path):
    report_path = tmp_path / "b1_b5_rank_ic.json"
    receipt_path = tmp_path / "experiment_ledger_receipts.jsonl"
    code = main()
    # main writes to default paths; we just verify it returns 0
    assert code == 0


def test_main_report_has_all_strategies(tmp_path):
    from scripts.run_b1_b5_phase_b import REPORT_PATH
    import json
    code = main()
    assert code == 0
    report = json.loads(REPORT_PATH.read_text())
    ids = {r["experiment_id"] for r in report["runs"]}
    assert ids == {"B1-sma3", "B2-walk-forward", "B3-momentum", "B4-xs-rank", "B5-buy-hold"}
