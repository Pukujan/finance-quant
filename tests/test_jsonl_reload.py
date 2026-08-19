from finance_quant.pit.fixtures import generate
from finance_quant.pit.manifest_store import ManifestJsonlStore


def test_jsonl_store_reloads_history_from_disk(tmp_path):
    path = tmp_path / "pit.jsonl"
    first = ManifestJsonlStore(path)
    for row in generate():
        first.put(row)
    pin = first.snapshot_pin()
    second = ManifestJsonlStore(path)
    assert second.snapshot_pin() == pin
    assert len(second.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")) == 1
