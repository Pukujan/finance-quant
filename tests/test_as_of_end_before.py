from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_end_before_all_rows_is_empty():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-02-01", "2024-02-01", {"close": 1}, "x", 0))
    assert store.as_of("bar", ["AAA"], "2024-01-01", "2024-01-15", "2024-02-01") == []
