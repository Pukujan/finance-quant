from finance_quant.pit.fixtures import DELIST_EFFECTIVE, DELIST_KNOWN, generate
from finance_quant.pit.store import MemoryGoldStore


def test_delisted_instrument_remains_queryable_after_effective_date():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    after = store.as_of("bar", ["ZZZ"], "2024-01-02", "2024-03-25", "2024-03-25")
    assert after, "delisted ZZZ must remain historically queryable (no survivorship erasure)"
    membership_before = store.as_of("universe", ["ZZZ"], "2024-01-02", "2024-02-01", "2024-02-01")
    membership_after_announce = store.as_of(
        "universe", ["ZZZ"], DELIST_EFFECTIVE.isoformat(), DELIST_EFFECTIVE.isoformat(),
        DELIST_KNOWN.isoformat(),
    )
    assert membership_before[0].payload["in_universe"] is True
    assert membership_after_announce[0].payload["in_universe"] is False
