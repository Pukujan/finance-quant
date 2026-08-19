"""PIT poison drills: missing, duplicate, and out-of-order bars must not silently invent facts."""
from __future__ import annotations

from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


def test_missing_bar_does_not_invent_a_close():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 10}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-04", "2024-01-04", {"close": 12}, "x", 0))
    mid = store.as_of("bar", ["AAA"], "2024-01-03", "2024-01-03", "2024-01-03")
    assert mid == []


def test_duplicate_revision_keeps_latest_known_as_of_kt():
    store = MemoryGoldStore()
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 10}, "x", 0))
    store.put(BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-03", {"close": 11}, "x", 1))
    early = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-02")
    late = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-02", "2024-01-03")
    assert early[0].payload["close"] == 10
    assert late[0].payload["close"] == 11


def test_out_of_order_ingest_does_not_change_as_of_visibility():
    store = MemoryGoldStore()
    later = BitemporalRecord("bar", "AAA", "2024-01-04", "2024-01-04", {"close": 12}, "x", 0)
    earlier = BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 10}, "x", 0)
    store.put(later)
    store.put(earlier)
    rows = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-04", "2024-01-04")
    assert [r.vt for r in rows] == ["2024-01-02", "2024-01-04"]
