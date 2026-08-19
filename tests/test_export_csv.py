from finance_quant.pit.fixtures import generate
from finance_quant.pit.export_csv import export_as_of_csv
from finance_quant.pit.store import MemoryGoldStore


def test_export_as_of_csv_roundtrip(tmp_path):
    store = MemoryGoldStore()
    for rec in generate():
        store.put(rec)
    path = export_as_of_csv(store, tmp_path / "out.csv", "bar", ["AAA"],
                            "2024-01-02", "2024-01-05", "2024-01-05")
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "namespace,instrument_id,vt,kt,revision,close"
    assert len(lines) == 5  # header + 4 business days
    assert all("AAA" in line for line in lines[1:])
