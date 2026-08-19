from finance_quant.search.random_lane import propose


def test_random_lane_count_matches_request():
    assert len(propose(3, 0)) == 0
    assert len(propose(3, 7)) == 7
