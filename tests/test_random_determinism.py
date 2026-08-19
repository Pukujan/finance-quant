from finance_quant.search.random_lane import propose


def test_random_lane_proposals_are_deterministic():
    assert propose(42, 5) == propose(42, 5)


def test_random_lane_different_seeds_differ():
    assert propose(42, 5) != propose(43, 5)


def test_random_lane_count_matches_request():
    assert len(propose(1, 7)) == 7
