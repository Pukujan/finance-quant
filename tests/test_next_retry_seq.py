from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_next_retry_seq_starts_at_zero_then_increments(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    assert store.next_retry_seq(wo.work_order_hash) == 0
    store.issue(wo, 0)
    assert store.next_retry_seq(wo.work_order_hash) == 1
    store.close()
