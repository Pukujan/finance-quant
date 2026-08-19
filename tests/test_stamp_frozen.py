from finance_quant.pit.stamps import DualStamp, daily_stamp


def test_dual_stamp_is_frozen():
    s = daily_stamp("2024-01-02")
    assert isinstance(s, DualStamp)
    try:
        s.tz = "UTC"
        assert False, "DualStamp must be frozen"
    except Exception:
        pass
