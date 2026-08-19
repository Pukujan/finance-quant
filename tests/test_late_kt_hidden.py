from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_does_not_return_rows_after_kt_bound_even_if_vt_in_range():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-10", {"close": 9}, "x", 0))
    assert store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-05") == []
