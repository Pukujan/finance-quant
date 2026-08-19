from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_does_not_return_later_vt_than_end():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-10", "2024-01-10", {"close": 2}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-05", "2024-01-10")
    assert [r.vt for r in rows] == ["2024-01-02"]
