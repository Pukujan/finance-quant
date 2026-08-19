from finance_quant.search.random_lane import propose
from finance_quant.dsl.checker import check


def test_random_lane_is_seeded_and_proposal_only():
    a, b = propose(7, 20), propose(7, 20)
    assert a == b
    assert all(p.authority == "propose_only" for p in a)
    assert all(check(p.expression).max_lookahead_days == 0 for p in a)
