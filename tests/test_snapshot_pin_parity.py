from finance_quant.pit.fixtures import generate
from finance_quant.pit.manifest_store import ManifestJsonlStore
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


def test_snapshot_pin_identical_across_three_v0_stores(tmp_path):
    gold = MemoryGoldStore()
    sqlite = SQLiteBitemporalStore(tmp_path / "pit.db")
    jsonl = ManifestJsonlStore(tmp_path / "pit.jsonl")
    for row in generate():
        gold.put(row)
        sqlite.put(row)
        jsonl.put(row)
    assert gold.snapshot_pin() == sqlite.snapshot_pin() == jsonl.snapshot_pin()
    sqlite.close()
