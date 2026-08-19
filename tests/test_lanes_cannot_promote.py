from finance_quant.search.random_lane import propose
from finance_quant.search.gp_lane import evolve


def test_search_lanes_cannot_promote():
    for p in propose(1, 3) + evolve(2, generations=1, population=2):
        assert p.authority == "propose_only"
        assert not hasattr(p, "promote")
