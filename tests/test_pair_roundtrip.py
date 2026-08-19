from finance_quant.dsl.ir import Field, RollingPair, from_dict, to_dict


def test_rolling_pair_round_trip():
    expr = RollingPair("corr", Field("close"), Field("volume"), 5)
    assert from_dict(to_dict(expr)) == expr
