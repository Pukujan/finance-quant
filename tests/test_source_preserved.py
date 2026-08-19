from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_source_field_is_preserved():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "vendor-x", 0))
    row = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")[0]
    assert row.source == "vendor-x"
