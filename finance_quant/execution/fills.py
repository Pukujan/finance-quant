"""Execution poison drills: same-bar fills are contracted failures, not fills."""
from __future__ import annotations

from dataclasses import dataclass

from .lean import ExecutionContract


class FillContractError(ValueError):
    pass


@dataclass(frozen=True)
class FillEvent:
    signal_bar: str
    fill_bar: str
    fill_time: str   # open | close | same_bar


def assert_fill_legal(event: FillEvent, contract: ExecutionContract = ExecutionContract()) -> None:
    if event.fill_time == "same_bar" or event.fill_bar == event.signal_bar:
        raise FillContractError(contract.daily_fill_rule)
    if event.fill_bar < event.signal_bar:
        raise FillContractError("fill before signal is impossible")
