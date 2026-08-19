from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_revisions_between_includes_late_restatements_only_in_window():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("fundamental", "AAA", "2023-12-31", "2024-02-14", {"revenue": 1}, "x", 0))
    store.put(BitemporalRecord("fundamental", "AAA", "2023-12-31", "2024-05-01", {"revenue": 2}, "x", 1))
    early = store.revisions_between("2024-01-01", "2024-03-01")
    late = store.revisions_between("2024-04-01", "2024-06-01")
    assert any(r.revision == 0 for r in early)
    assert any(r.revision == 1 for r in late)
    assert all(r.kt <= "2024-03-01" for r in early)
