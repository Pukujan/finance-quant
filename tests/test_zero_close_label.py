from finance_quant.pit.labels import next_day_returns
from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_next_day_return_skips_zero_close():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 0.0}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-03", "2024-01-03", {"close": 1.0}, "x", 0))
    rets = next_day_returns(store, "AAA", ["2024-01-02", "2024-01-03"], "2024-01-03")
    assert "2024-01-02" not in rets
