from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_ingest_run_id_is_preserved():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0,
                               ingest_run_id="ingest-9"))
    row = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")[0]
    assert row.ingest_run_id == "ingest-9"
