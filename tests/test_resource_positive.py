from finance_quant.orchestration.contracts import ResourceRequest
import pytest


def test_resource_request_requires_positive_cpu_and_memory():
    with pytest.raises(Exception):
        ResourceRequest(cpu=0, mem_mb=64, wall_timeout_s=10, heartbeat_s=1)
    with pytest.raises(Exception):
        ResourceRequest(cpu=1, mem_mb=0, wall_timeout_s=10, heartbeat_s=1)
