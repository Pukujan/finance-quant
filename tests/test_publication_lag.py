from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_fundamental_publication_lag_hides_value_until_known_at():
    store = MemoryGoldStore()
    store.put(BitemporalRecord(
        "fundamental", "AAA", "2023-12-31", "2024-02-14",
        {"revenue": 1000}, "vendor", 0,
    ))
    before = store.as_of("fundamental", ["AAA"], "2023-12-31", "2023-12-31", "2024-01-01")
    after = store.as_of("fundamental", ["AAA"], "2023-12-31", "2023-12-31", "2024-02-14")
    assert before == []
    assert after[0].payload["revenue"] == 1000
