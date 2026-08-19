from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_equivalent_resource_requests_do_not_fork_work_order_identity():
    a = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    b = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(cpu=1), fold_id="k")
    assert a.work_order_hash == b.work_order_hash
