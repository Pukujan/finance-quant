from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_preserves_payload_fields():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02",
                               {"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 10}, "x", 0))
    row = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")[0]
    assert row.payload["high"] == 2.0
    assert row.payload["volume"] == 10
