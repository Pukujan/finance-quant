from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_unknown_instrument_as_of_is_empty():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    assert store.as_of("bar", ["NOT_A_SYMBOL"], "2024-01-02", "2024-03-01", "2024-03-01") == []
