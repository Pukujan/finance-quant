from finance_quant.pit.labels import rank_ic


def test_rank_ic_perfect_agreement_is_one():
    assert abs(rank_ic({"A": 1.0, "B": 2.0, "C": 3.0}, {"A": 0.1, "B": 0.2, "C": 0.3}) - 1.0) < 1e-9


def test_rank_ic_empty_or_single_is_zero():
    assert rank_ic({}, {}) == 0.0
    assert rank_ic({"A": 1.0}, {"A": 0.1}) == 0.0
