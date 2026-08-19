from finance_quant.orchestration.lifecycle import AttemptStore
from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_second_issue_of_identical_work_order_is_not_a_new_authority(tmp_path):
    store = AttemptStore(tmp_path / "a.db")
    wo = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    assert store.issue(wo) is True
    assert store.issue(wo) is False
    store.close()
