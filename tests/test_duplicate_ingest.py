from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore
import pytest


def test_sqlite_rejects_duplicate_primary_key_ingest(tmp_path):
    store = SQLiteBitemporalStore(tmp_path / "pit.db")
    row = BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0)
    store.put(row)
    with pytest.raises(Exception):
        store.put(row)
    store.close()
