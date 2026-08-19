from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_as_of_empty_instrument_list_returns_empty():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    assert store.as_of("bar", [], "2024-01-02", "2024-03-01", "2024-03-01") == []
