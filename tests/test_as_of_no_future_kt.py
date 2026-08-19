from datetime import date, timedelta

from hypothesis import given, settings, strategies as st

from finance_quant.pit.model import BitemporalRecord
from finance_quant.pit.store import MemoryGoldStore


@settings(max_examples=60)
@given(
    n=st.integers(min_value=1, max_value=20),
    kt_day=st.integers(min_value=0, max_value=30),
)
def test_as_of_never_returns_unknown_knowledge(n, kt_day):
    store = MemoryGoldStore()
    base = date(2024, 1, 1)
    bound = (base + timedelta(days=kt_day)).isoformat()
    for i in range(n):
        store.put(BitemporalRecord(
            "bar", "AAA", (base + timedelta(days=i)).isoformat(),
            (base + timedelta(days=i)).isoformat(), {"close": float(i)}, "x", 0,
        ))
    rows = store.as_of("bar", ["AAA"], base.isoformat(), (base + timedelta(days=n)).isoformat(), bound)
    assert all(r.kt <= bound for r in rows)
