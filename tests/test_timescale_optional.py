import os

import pytest

from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore
from finance_quant.pit.timescale import TimescalePITStore, timescale_dsn


@pytest.mark.skipif(not timescale_dsn(), reason="FQ_TIMESCALE_DSN not set")
def test_timescale_matches_gold_when_available():
    gold = MemoryGoldStore()
    store = TimescalePITStore(timescale_dsn())
    try:
        for row in generate()[:40]:
            gold.put(row)
            store.put(row)
        assert store.snapshot_pin() == gold.snapshot_pin()
        early = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-05", "2024-01-05")
        assert [r.canonical() for r in early] == [
            r.canonical() for r in gold.as_of("bar", ["AAA"], "2024-01-02", "2024-01-05", "2024-01-05")
        ]
    finally:
        store.close()
