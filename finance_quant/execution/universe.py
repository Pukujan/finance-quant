"""Stale and delisted instruments cannot receive new order intent."""
from __future__ import annotations

from dataclasses import dataclass


class InstrumentHalted(Exception):
    pass


@dataclass(frozen=True)
class InstrumentState:
    instrument_id: str
    in_universe: bool
    halted: bool
    delisted: bool


def assert_tradable(state: InstrumentState) -> None:
    if state.halted or state.delisted or not state.in_universe:
        raise InstrumentHalted(state.instrument_id)
