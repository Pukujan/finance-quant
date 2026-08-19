from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder
from finance_quant.orchestration.lifecycle import AttemptState, AttemptStore, LifecycleError
import pytest

FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=30.0, heartbeat_s=0.5)


def test_queued_attempt_can_cancel_running_cannot(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "finance_quant.orchestration.handlers:run", "s", "0" * 40,
                   (1,), "m" * 64, FAST, fold_id="k")
    store.issue(wo)
    store.mark_queued(wo.work_order_hash)
    store.cancel(wo.work_order_hash)
    assert store.last_state(wo.work_order_hash) is AttemptState.CANCELLED
    wo2 = WorkOrder("c", "finance_quant.orchestration.handlers:run", "s", "0" * 40,
                    (2,), "m" * 64, FAST, fold_id="k2")
    store.issue(wo2)
    store.mark_queued(wo2.work_order_hash)
    store.mark_running(wo2.work_order_hash)
    with pytest.raises(LifecycleError):
        store.cancel(wo2.work_order_hash)
    store.close()
