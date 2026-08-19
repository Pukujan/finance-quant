from finance_quant.pit.store import SQLiteBitemporalStore
from finance_quant.pit.model import BitemporalRecord


def test_sqlite_as_of_empty_instruments(tmp_path):
    store = SQLiteBitemporalStore(tmp_path / "pit.db")
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0))
    assert store.as_of("bar", [], "2024-01-02", "2024-01-02", "2024-01-02") == []
    store.close()
