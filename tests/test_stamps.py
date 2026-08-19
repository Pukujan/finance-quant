import pytest

from finance_quant.pit.stamps import daily_stamp


def test_daily_stamp_rejects_naive_datetimes_and_is_iso():
    s = daily_stamp("2024-03-11")
    assert s.exchange_local_date == s.utc_date == "2024-03-11"
    assert s.tz == "America/New_York"
    with pytest.raises(ValueError):
        daily_stamp("2024-03-11T00:00:00")
