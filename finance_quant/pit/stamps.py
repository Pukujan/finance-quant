"""Timestamps are ISO calendar dates plus an explicit timezone label. No naive local midnight."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DualStamp:
    exchange_local_date: str
    utc_date: str
    tz: str


def daily_stamp(iso_date: str, tz: str = "America/New_York") -> DualStamp:
    if len(iso_date) != 10 or iso_date[4] != "-" or iso_date[7] != "-":
        raise ValueError("expected YYYY-MM-DD")
    return DualStamp(iso_date, iso_date, tz)
