"""Resource pool sizing + per-attempt limits for the local backend."""
from __future__ import annotations

import os
from dataclasses import dataclass

from .contracts import ResourceRequest


@dataclass(frozen=True)
class PoolLimits:
    concurrency: int
    stdout_stderr_cap_bytes: int = 1 << 20   # 1 MiB ring capture
    cancel_grace_s: float = 10.0

    @staticmethod
    def conservative() -> "PoolLimits":
        cpus = os.cpu_count() or 2
        return PoolLimits(concurrency=max(1, cpus - 1))


def pool_fits(limits: PoolLimits, request: ResourceRequest) -> bool:
    return request.cpu <= max(1, (os.cpu_count() or 1))
