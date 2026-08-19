from finance_quant.dsl.ir import Field, Unary, from_dict, to_dict


def test_unary_round_trip():
    expr = Unary("abs", Unary("neg", Field("close")))
    assert from_dict(to_dict(expr)) == expr
