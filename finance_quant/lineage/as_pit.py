"""Graph edges as ordinary PIT records: derived features cannot manufacture history."""
from __future__ import annotations

from finance_quant.lineage.graph import GraphEdge
from finance_quant.pit.model import BitemporalRecord


def edge_to_record(edge: GraphEdge) -> BitemporalRecord:
    return BitemporalRecord(
        namespace="universe",
        instrument_id=f"{edge.src}->{edge.dst}",
        vt=edge.valid_from,
        kt=edge.known_at,
        payload={"kind": edge.kind, "src": edge.src, "dst": edge.dst, "valid_to": edge.valid_to},
        source="graph-fixture",
        revision=0,
    )
