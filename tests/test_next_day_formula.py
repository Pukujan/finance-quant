from finance_quant.pit.labels import next_day_returns
from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_next_day_return_formula():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 10.0}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-03", "2024-01-03", {"close": 11.0}, "x", 0))
    rets = next_day_returns(store, "AAA", ["2024-01-02", "2024-01-03"], "2024-01-03")
    assert abs(rets["2024-01-02"] - 0.1) < 1e-12
