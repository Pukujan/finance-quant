from finance_quant.lineage.as_pit import edge_to_record
from finance_quant.lineage.graph import STATIC_FIXTURE
from finance_quant.pit.store import MemoryGoldStore


def test_graph_edges_as_pit_records_obey_known_at():
    store = MemoryGoldStore()
    for edge in STATIC_FIXTURE:
        store.put(edge_to_record(edge))
    early = store.as_of("universe", ["CCC->DDD"], "2024-01-01", "2024-12-31", "2024-02-01")
    late = store.as_of("universe", ["CCC->DDD"], "2024-01-01", "2024-12-31", "2024-03-15")
    assert early == []
    assert late[0].payload["kind"] == "supplier"
