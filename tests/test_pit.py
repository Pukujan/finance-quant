from __future__ import annotations

from datetime import date, timedelta

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from finance_quant.pit.bakeoff import BakeoffHarness
from finance_quant.pit.fixtures import SYMBOLS, business_days, generate
from finance_quant.pit.model import BitemporalRecord, PitContractError
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


@pytest.fixture()
def stores(tmp_path):
    gold = MemoryGoldStore()
    sqlite = SQLiteBitemporalStore(tmp_path / "pit.db")
    rows = generate()
    for row in rows:
        gold.put(row)
        sqlite.put(row)
    yield gold, sqlite
    sqlite.close()


def test_fixture_bakeoff_q1_q8_matches_gold(stores):
    gold, sqlite = stores
    results = BakeoffHarness(sqlite, gold, business_days(date(2024, 1, 2), 60)).run_all()
    assert {r.query_id for r in results} == {"Q1", "Q2", "Q3", "Q4a", "Q4b", "Q5", "Q6", "Q7", "Q8"}
    assert all(r.passed_oracle for r in results)


def test_restated_fundamental_is_not_visible_before_its_knowledge_time(stores):
    gold, sqlite = stores
    early = sqlite.as_of("fundamental", ["AAA"], "2023-01-01", "2023-12-31", "2024-02-15")
    late = sqlite.as_of("fundamental", ["AAA"], "2023-01-01", "2023-12-31", "2024-06-01")
    assert len(early) == len(late) == 2
    assert any(r.revision == 0 for r in early)
    assert any(r.revision == 1 for r in late)
    assert sqlite.snapshot_pin() == gold.snapshot_pin()


def test_immutable_history_rejects_overwrite(tmp_path):
    store = SQLiteBitemporalStore(tmp_path / "pit.db")
    row = BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {"close": 1}, "x", 0)
    store.put(row)
    with pytest.raises(Exception):
        store.put(row)
    store.close()


@settings(max_examples=80, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    n=st.integers(min_value=1, max_value=40),
    query_day=st.integers(min_value=0, max_value=45),
    kt_day=st.integers(min_value=0, max_value=55),
)
def test_as_of_sqlite_matches_gold_on_generated_revision_histories(tmp_path, n, query_day, kt_day):
    """FQ-PROP-002 T1 oracle: arbitrary revisions, randomized query clocks."""
    gold = MemoryGoldStore()
    sqlite = SQLiteBitemporalStore(tmp_path / f"pit-{n}-{query_day}-{kt_day}.db")
    base = date(2024, 1, 1)
    for i in range(n):
        vt = (base + timedelta(days=i % 12)).isoformat()
        kt = (base + timedelta(days=i)).isoformat()
        rec = BitemporalRecord(
            "bar", SYMBOLS[i % len(SYMBOLS)], vt, kt,
            {"close": i}, "generated", i // 12,
        )
        gold.put(rec)
        sqlite.put(rec)
    cutoff = (base + timedelta(days=kt_day)).isoformat()
    end = (base + timedelta(days=query_day)).isoformat()
    expected = gold.as_of("bar", SYMBOLS, base.isoformat(), end, cutoff)
    actual = sqlite.as_of("bar", SYMBOLS, base.isoformat(), end, cutoff)
    assert [r.canonical() for r in actual] == [r.canonical() for r in expected]
    sqlite.close()


def test_contract_rejects_missing_knowledge_time():
    with pytest.raises(PitContractError):
        BitemporalRecord("bar", "AAA", "2024-01-01", "", {}, "x", 0)
