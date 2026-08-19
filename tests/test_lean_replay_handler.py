from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder
from finance_quant.orchestration.executor import run_work_order


def test_lean_replay_handler_emits_algorithm_hash(tmp_path):
    wo = WorkOrder(
        "c", "finance_quant.orchestration.handlers:lean_replay", "snap",
        "0" * 40, (1,), "m" * 64,
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
        fold_id="k1", replay_id="raw-v0",
    )
    a = run_work_order(wo, tmp_path / "a", "w", "local")
    b = run_work_order(wo, tmp_path / "b", "w", "local")
    assert a.terminal_status.value == "completed"
    assert dict(a.metrics)["contract"] == 64.0
    assert len(a.artifact_manifest) == 1
    assert a.artifact_manifest[0].sha256 == b.artifact_manifest[0].sha256
