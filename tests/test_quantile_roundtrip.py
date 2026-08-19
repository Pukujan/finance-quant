from finance_quant.dsl.ir import Field, Rolling, from_dict, to_dict


def test_quantile_round_trip():
    expr = Rolling("quantile", Field("close"), 7)
    assert from_dict(to_dict(expr)) == expr
