from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_revision_zero_is_visible_when_it_is_the_latest_known():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")
    assert rows[0].revision == 0
