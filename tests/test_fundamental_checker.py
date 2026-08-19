from finance_quant.dsl.checker import check
from finance_quant.dsl.ir import Fundamental


def test_fundamental_with_sufficient_lag_is_accepted():
    assert check(Fundamental("revenue", 45)).max_lookahead_days == 0
    assert check(Fundamental("revenue", 90)).max_lookahead_days == 0
