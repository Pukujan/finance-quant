from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_price_spike_is_still_as_of_visible_not_silently_clipped():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 10.0}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-03", "2024-01-03", {"close": 1000.0}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-03", "2024-01-03")
    assert rows[1].payload["close"] == 1000.0
