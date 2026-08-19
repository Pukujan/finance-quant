"""Seal use counters: SEAL-A max 2, SEAL-B max 1. Exceeding is invalid."""
from __future__ import annotations

from .seal import SealRecord


class SealExhausted(Exception):
    pass


def assert_use_allowed(record: SealRecord, use_number: int) -> None:
    if use_number < 1 or use_number > record.max_uses:
        raise SealExhausted(f"{record.case_set_id} use {use_number} > max {record.max_uses}")
