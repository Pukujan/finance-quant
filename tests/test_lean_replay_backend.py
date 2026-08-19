from finance_quant.orchestration.backends.local import CrashReport, LocalBackend
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_lean_replay_survives_local_backend():
    wo = WorkOrder(
        "c", "finance_quant.orchestration.handlers:lean_replay", "snap",
        "0" * 40, (1,), "m" * 64,
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
        fold_id="k1", replay_id="raw-v0",
    )
    outcome = LocalBackend().execute(wo)
    assert not isinstance(outcome, CrashReport), getattr(outcome, "detail", "")
    assert dict(outcome.metrics)["contract"] == 64.0
    assert outcome.artifact_manifest
