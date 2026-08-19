from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_start_before_first_row_still_returns_later_in_range():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-10", "2024-01-10", {"close": 1}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-01", "2024-01-31", "2024-01-31")
    assert [r.vt for r in rows] == ["2024-01-10"]
