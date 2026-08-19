"""Retry policy: never in-place resurrection; retry = new attempt row (retry_seq+1)."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import TerminalStatus


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    retry_on: frozenset[TerminalStatus] = frozenset(
        {TerminalStatus.FAILED, TerminalStatus.CRASHED}
    )
    backoff_s: float = 0.0

    def should_retry(self, status: TerminalStatus, retries_used: int) -> bool:
        return status in self.retry_on and retries_used < self.max_retries
