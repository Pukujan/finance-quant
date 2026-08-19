from finance_quant.orchestration.resources import PoolLimits, pool_fits
from finance_quant.orchestration.contracts import ResourceRequest


def test_pool_rejects_oversize_cpu_request():
    limits = PoolLimits(concurrency=2)
    assert pool_fits(limits, ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=10, heartbeat_s=1))
    assert not pool_fits(limits, ResourceRequest(cpu=10_000, mem_mb=64, wall_timeout_s=10, heartbeat_s=1))
