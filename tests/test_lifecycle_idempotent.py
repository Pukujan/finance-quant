import pytest

from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder
from finance_quant.orchestration.lifecycle import AttemptState, AttemptStore, LifecycleError


def _wo(task_type="t"):
    return WorkOrder(
        campaign_id="c",
        task_type=task_type,
        dataset_snapshot_id="snap",
        code_commit="0" * 40,
        seeds=(1,),
        manifest_hash="m" * 64,
        resource_request=ResourceRequest(wall_timeout_s=5.0, heartbeat_s=1.0),
    )


def test_issue_same_work_order_twice_is_idempotent(tmp_path):
    store = AttemptStore(tmp_path / "ledger.db")
    wo = _wo()
    assert store.issue(wo) is True
    assert store.issue(wo) is False
    store.close()


def test_invalid_state_transition_raises(tmp_path):
    store = AttemptStore(tmp_path / "ledger.db")
    wo = _wo()
    store.issue(wo)
    store.mark_queued(wo.work_order_hash)
    store.mark_running(wo.work_order_hash)
    with pytest.raises(LifecycleError):
        store.mark_queued(wo.work_order_hash)
    store.close()
