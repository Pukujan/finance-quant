from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_filters_by_instrument_list_exactly():
    store = MemoryGoldStore()
    for sym in ("AAA", "BBB", "CCC"):
        store.put(BitemporalRecord("bar", sym, "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    rows = store.as_of("bar", ["BBB"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert [r.instrument_id for r in rows] == ["BBB"]
