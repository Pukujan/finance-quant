from finance_quant.search.overfit import search_artifact
from finance_quant.search.random_lane import propose
from finance_quant.search.gp_lane import evolve


def test_scorecard_lanes_remain_propose_only():
    assert all(p.authority == "propose_only" for p in propose(1, 4) + evolve(2, 1, 3))
    assert search_artifact([0.0] * 10 + [0.001])
