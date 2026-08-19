from finance_quant.pit.export_csv import export_as_of_csv
from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_csv_export_is_derived_and_as_of(tmp_path):
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    path = export_as_of_csv(store, tmp_path / "extract.csv", "bar", ["AAA"],
                            "2024-01-02", "2024-01-05", "2024-01-05")
    text = path.read_text(encoding="utf-8")
    assert "namespace,instrument_id,vt,kt,revision,close" in text
    assert "AAA" in text
    assert "ZZZ" not in text
