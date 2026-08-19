from finance_quant.orchestration.authority import CapabilityClass, worker_environment


def test_backend_choice_does_not_appear_in_work_order_hash_inputs():
    """Invariant 11: backend is not part of WorkOrder identity."""
    from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder
    a = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    b = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(), fold_id="k")
    assert a.work_order_hash == b.work_order_hash
    env = worker_environment(CapabilityClass.RESEARCH_WORKER, {"PATH": "x"})
    assert "FQ_BACKEND" not in env
