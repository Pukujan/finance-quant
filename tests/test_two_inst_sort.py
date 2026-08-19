from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_same_vt_two_instruments_sorted():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "ZZZ", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 2}, "x", 0))
    rows = store.as_of("bar", ["ZZZ", "AAA"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert [r.instrument_id for r in rows] == ["AAA", "ZZZ"]
