from finance_quant.orchestration.contracts import ResourceRequest
import pytest


def test_heartbeat_must_be_strictly_less_than_wall_timeout():
    with pytest.raises(Exception):
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=5, heartbeat_s=5)
    with pytest.raises(Exception):
        ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=5, heartbeat_s=6)
    ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=5, heartbeat_s=1)
