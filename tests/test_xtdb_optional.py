import pytest

from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore
from finance_quant.pit.xtdb import XTDBPITStore, xtdb_dsn


@pytest.mark.skipif(not xtdb_dsn(), reason="FQ_XTDB_DSN not set")
def test_xtdb_matches_gold_when_available():
    gold = MemoryGoldStore()
    store = XTDBPITStore(xtdb_dsn())
    try:
        for row in generate()[:20]:
            gold.put(row)
            store.put(row)
        assert store.snapshot_pin() == gold.snapshot_pin()
    finally:
        store.close()
