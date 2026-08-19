from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_five_days_returns_five_rows():
    store = MemoryGoldStore()
    days = [f"2024-01-0{i}" for i in range(2, 7)]
    for i, d in enumerate(days, 1):
        store.put(BitemporalRecord("bar", "AAA", d, d, {"close": i}, "x", 0))
    rows = store.as_of("bar", ["AAA"], days[0], days[-1], days[-1])
    assert len(rows) == 5
