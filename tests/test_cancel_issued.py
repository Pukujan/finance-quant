from finance_quant.orchestration.lifecycle import AttemptState, AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_issued_attempt_can_be_cancelled(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    store.issue(wo)
    store.cancel(wo.work_order_hash)
    assert store.last_state(wo.work_order_hash) is AttemptState.CANCELLED
    store.close()
