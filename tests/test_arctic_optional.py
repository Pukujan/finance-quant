import pytest

from finance_quant.pit.arctic import ArcticPITStore, arcticdb_available
from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


@pytest.mark.skipif(not arcticdb_available(), reason="arcticdb not installed")
def test_arctic_matches_gold_when_available(tmp_path):
    gold = MemoryGoldStore()
    store = ArcticPITStore(uri=f"lmdb://{tmp_path / 'adb'}")
    for row in generate()[:20]:
        gold.put(row)
        store.put(row)
    assert store.snapshot_pin() == gold.snapshot_pin()
