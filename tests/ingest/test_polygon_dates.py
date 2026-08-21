from datetime import datetime, timedelta, timezone

from finance_quant.ingest.polygon import _iso, _to_utc_ms, _utcnow


def test_iso_treats_naive_datetime_as_utc():
    value = datetime(2024, 1, 2, 3, 4, 5, 678901)

    assert _iso(value) == "2024-01-02T03:04:05.678901+00:00"


def test_iso_converts_timezone_aware_datetime_to_utc():
    value = datetime(
        2024, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=-5))
    )

    assert _iso(value) == "2024-01-02T08:04:05+00:00"


def test_to_utc_ms_converts_epoch_milliseconds():
    value = _to_utc_ms(1704164645678)

    assert value == datetime(2024, 1, 2, 3, 4, 5, 678000, tzinfo=timezone.utc)


def test_utcnow_returns_utc_datetime():
    value = _utcnow()

    assert value.tzinfo is not None
    assert value.utcoffset() == timedelta(0)
