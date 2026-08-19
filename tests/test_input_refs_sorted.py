from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder


def test_input_refs_are_sorted_canonically():
    a = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(),
                  input_refs=(("b", "2"), ("a", "1")))
    b = WorkOrder("c", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest(),
                  input_refs=(("a", "1"), ("b", "2")))
    assert a.work_order_hash == b.work_order_hash
    assert a.input_refs == (("a", "1"), ("b", "2"))
