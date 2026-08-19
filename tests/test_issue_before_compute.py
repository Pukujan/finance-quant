from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_issue_creates_row_before_any_running_state(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    assert store.issue(wo) is True
    assert store.last_state(wo.work_order_hash).value == "issued"
    store.close()
