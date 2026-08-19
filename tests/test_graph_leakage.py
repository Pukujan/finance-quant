from finance_quant.lineage.graph import GraphEdge, as_of_edges


def test_graph_feature_cannot_use_late_announced_edge():
    edges = [
        GraphEdge("AAA", "BBB", "sector_peer", "2024-01-01", "2024-12-31", "2024-01-01"),
        GraphEdge("CCC", "DDD", "supplier", "2024-01-01", "2024-12-31", "2024-03-15"),
    ]
    as_of_feb = as_of_edges(edges, "2024-02-01", "2024-02-01")
    assert ("CCC", "DDD") not in {(e.src, e.dst) for e in as_of_feb}
    as_of_apr = as_of_edges(edges, "2024-04-01", "2024-04-01")
    assert ("CCC", "DDD") in {(e.src, e.dst) for e in as_of_apr}
