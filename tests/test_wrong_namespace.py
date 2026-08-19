from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_unknown_namespace_is_empty():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    assert store.as_of("macro", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02") == []
