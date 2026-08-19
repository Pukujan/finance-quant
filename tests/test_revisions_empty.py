from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_revisions_between_empty_window_is_empty():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    assert store.revisions_between("1999-01-01", "1999-01-02") == []
