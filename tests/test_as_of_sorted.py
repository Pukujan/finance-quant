from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_multiple_instruments_as_of_are_sorted():
    store = MemoryGoldStore()
    for sym in ("CCC", "AAA", "BBB"):
        store.put(BitemporalRecord("bar", sym, "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    rows = store.as_of("bar", ["BBB", "AAA", "CCC"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert [r.instrument_id for r in rows] == ["AAA", "BBB", "CCC"]
