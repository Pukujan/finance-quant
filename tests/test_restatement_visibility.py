import pytest

from finance_quant.pit.bakeoff import BakeoffHarness
from finance_quant.pit.fixtures import N_DAYS, START, business_days, generate
from finance_quant.pit.store import MemoryGoldStore, SQLiteBitemporalStore


def test_restatement_changes_fundamentals_between_knowledge_times(tmp_path):
    oracle = MemoryGoldStore()
    target = SQLiteBitemporalStore(tmp_path / "pit.db")
    for rec in generate():
        oracle.put(rec)
        target.put(rec)
    days = business_days(START, N_DAYS)
    harness = BakeoffHarness(target, oracle, days)
    results = {r.query_id: r for r in harness.run_all()}
    assert results["Q4a"].passed_oracle
    assert results["Q4b"].passed_oracle
    assert results["Q4a"].fingerprint != results["Q4b"].fingerprint
    target.close()
