from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_does_not_return_other_namespace_rows():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("fundamental", "AAA", "2024-01-02", "2024-01-02", {"revenue": 9}, "x", 0))
    bars = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert all(r.namespace == "bar" for r in bars)
    assert bars[0].payload["close"] == 1
