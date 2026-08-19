from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_last_state_none_for_unknown_attempt(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    assert store.last_state("deadbeef" * 8) is None
    store.issue(wo)
    assert store.last_state(wo.work_order_hash) is not None
    store.close()
