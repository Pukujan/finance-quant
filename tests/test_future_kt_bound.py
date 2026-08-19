from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_future_kt_bound_includes_all_known_rows():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2099-01-01")
    assert len(rows) == 1
