from finance_quant.pit.store import MemoryGoldStore
from finance_quant.pit.model import BitemporalRecord


def test_as_of_end_exclusive_is_not_the_contract_inclusive_end():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-03", "2024-01-03", {"close": 2}, "x", 0))
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-03")
    assert [r.vt for r in rows] == ["2024-01-02"]
