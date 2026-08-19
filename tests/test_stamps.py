import pytest

from finance_quant.pit.stamps import DualStamp, daily_stamp


def test_daily_stamp_returns_dual_stamp():
    stamp = daily_stamp("2024-01-02")
    assert stamp == DualStamp("2024-01-02", "2024-01-02", "America/New_York")


def test_daily_stamp_accepts_custom_tz():
    stamp = daily_stamp("2024-01-02", tz="UTC")
    assert stamp.tz == "UTC"


def test_daily_stamp_rejects_malformed_date():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        daily_stamp("2024-1-02")
