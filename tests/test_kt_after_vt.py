from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_kt_after_vt_is_allowed_for_lagged_fundamentals():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("fundamental", "AAA", "2023-12-31", "2024-02-14", {"revenue": 1}, "x", 0))
    assert store.as_of("fundamental", ["AAA"], "2023-12-31", "2023-12-31", "2024-02-13") == []
    assert store.as_of("fundamental", ["AAA"], "2023-12-31", "2023-12-31", "2024-02-14")[0].payload["revenue"] == 1
