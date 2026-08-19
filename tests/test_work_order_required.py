from finance_quant.orchestration.contracts import ResourceRequest, WorkOrder
import pytest


def test_work_order_requires_seed_and_manifest():
    with pytest.raises(Exception):
        WorkOrder("c", "t", "d", "0" * 40, (), "m" * 64, ResourceRequest())
    with pytest.raises(Exception):
        WorkOrder("", "t", "d", "0" * 40, (1,), "m" * 64, ResourceRequest())
