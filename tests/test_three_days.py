from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_three_days_returns_three_rows():
    store = MemoryGoldStore()
    for d, px in (("2024-01-02", 1), ("2024-01-03", 2), ("2024-01-04", 3)):
        store.put(BitemporalRecord("bar", "AAA", d, d, {"close": px}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-04", "2024-01-04")
    assert [r.payload["close"] for r in rows] == [1, 2, 3]
