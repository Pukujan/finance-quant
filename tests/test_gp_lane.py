from finance_quant.dsl.checker import check
from finance_quant.search.gp_lane import evolve


def test_gp_lane_is_seeded_and_checker_clean():
    assert evolve(4) == evolve(4)
    assert all(p.authority == "propose_only" and check(p.expression).max_lookahead_days == 0
               for p in evolve(4))
