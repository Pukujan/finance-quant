from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_does_not_mix_instruments():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("bar", "BBB", "2024-01-02", "2024-01-02", {"close": 9}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert [r.instrument_id for r in rows] == ["AAA"]
    assert rows[0].payload["close"] == 1
