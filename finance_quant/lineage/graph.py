"""PIT-safe static graph fixture and AS-OF edge filtering (spike #6 boundary rule 1-2)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GraphEdge:
    src: str
    dst: str
    kind: str
    valid_from: str
    valid_to: str
    known_at: str


def as_of_edges(edges: list[GraphEdge], vt: str, kt: str) -> list[GraphEdge]:
    """Filter BEFORE projection/aggregation: late-known edges cannot manufacture history."""
    return sorted((e for e in edges if e.valid_from <= vt <= e.valid_to and e.known_at <= kt),
                  key=lambda e: (e.src, e.dst, e.kind))


STATIC_FIXTURE = [
    GraphEdge("AAA", "BBB", "sector_peer", "2024-01-01", "2024-12-31", "2024-01-01"),
    # The relationship was valid earlier but public only after the disclosure date.
    GraphEdge("CCC", "DDD", "supplier", "2024-01-01", "2024-12-31", "2024-03-15"),
]
