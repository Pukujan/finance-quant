from finance_quant.search.gp_lane import evolve


def test_gp_different_seeds_differ():
    a = [p.expression_hash for p in evolve(1, 1, 4)]
    b = [p.expression_hash for p in evolve(2, 1, 4)]
    assert a != b
