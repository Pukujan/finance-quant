from finance_quant.pit.fixtures import N_DAYS, START, business_days, generate


def test_fixture_has_restatements_and_delist_and_split():
    rows = generate()
    assert any(r.source == "fixture-restatement" for r in rows)
    assert any(r.namespace == "corporate_action" and r.payload.get("kind") == "split" for r in rows)
    assert any(r.namespace == "universe" and r.payload.get("in_universe") is False for r in rows)
    assert len(business_days(START, N_DAYS)) == N_DAYS
