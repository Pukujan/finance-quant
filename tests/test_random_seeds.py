from finance_quant.search.random_lane import propose


def test_different_seeds_produce_different_proposal_sets():
    a = [p.expression_hash for p in propose(1, 8)]
    b = [p.expression_hash for p in propose(2, 8)]
    assert a != b
