from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_four_days_returns_four_rows():
    store = MemoryGoldStore()
    days = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    for i, d in enumerate(days, 1):
        store.put(BitemporalRecord("bar", "AAA", d, d, {"close": i}, "x", 0))
    rows = store.as_of("bar", ["AAA"], days[0], days[-1], days[-1])
    assert [r.payload["close"] for r in rows] == [1, 2, 3, 4]
