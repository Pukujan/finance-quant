from finance_quant.orchestration.backends.local import CrashReport, LocalBackend
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_feature_eval_survives_local_backend_subprocess():
    wo = WorkOrder(
        "c", "finance_quant.orchestration.handlers:feature_eval", "snap",
        "0" * 40, (7,), "m" * 64,
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=20, heartbeat_s=0.5),
        fold_id="B2-F1",
    )
    outcome = LocalBackend().execute(wo)
    assert not isinstance(outcome, CrashReport), getattr(outcome, "detail", "")
    assert dict(outcome.metrics)["sma3"] == 10.0
