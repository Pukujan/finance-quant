from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_skips_gap_day():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-04", "2024-01-04", {"close": 3}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-04", "2024-01-04")
    assert [r.vt for r in rows] == ["2024-01-02", "2024-01-04"]
