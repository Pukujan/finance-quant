from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_macro_namespace_is_as_of_queryable():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("macro", "VIX", "2024-01-02", "2024-01-02", {"close": 14.0}, "x", 0))
    rows = store.as_of("macro", ["VIX"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert rows[0].payload["close"] == 14.0
    assert store.as_of("macro", ["VIX"], "2024-01-02", "2024-01-02", "2023-12-31") == []
