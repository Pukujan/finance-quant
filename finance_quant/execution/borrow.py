"""Shorts require explicit borrow. Infinite borrow at zero cost is a named debug model only."""
from __future__ import annotations

from dataclasses import dataclass


class BorrowUnavailable(Exception):
    pass


@dataclass(frozen=True)
class BorrowModel:
    name: str
    available: bool
    cost_bps: float


DEBUG_INFINITE_ZERO = BorrowModel("debug_infinite_zero", True, 0.0)
DEFAULT = BorrowModel("explicit_required", False, 0.0)


def assert_short_allowed(model: BorrowModel, side: str) -> None:
    if side == "sell" and not model.available:
        raise BorrowUnavailable(model.name)
