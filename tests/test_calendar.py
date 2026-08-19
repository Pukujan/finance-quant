"""Calendar/timezone boundary: evaluation days are ISO dates, never naive local midnight."""
from __future__ import annotations

from datetime import date, timedelta

from finance_quant.pit.fixtures import business_days


def test_business_days_skip_weekends_and_are_iso():
    days = business_days(date(2024, 1, 5), 5)  # Friday
    assert days[0] == "2024-01-05"
    assert "2024-01-06" not in days  # Saturday
    assert "2024-01-07" not in days  # Sunday
    assert days[1] == "2024-01-08"
    assert all(len(d) == 10 and d[4] == "-" and d[7] == "-" for d in days)


def test_dst_adjacent_dates_remain_plain_iso_calendar_days():
    # US DST 2024-03-10 was Sunday; daily PIT uses calendar business days, not 23h/25h bars.
    around = business_days(date(2024, 3, 8), 5)
    assert around[0] == "2024-03-08"
    assert "2024-03-10" not in around
    assert around[1] == "2024-03-11"
    assert around == sorted(around)
    assert date.fromisoformat(around[-1]) - date.fromisoformat(around[0]) >= timedelta(days=4)
