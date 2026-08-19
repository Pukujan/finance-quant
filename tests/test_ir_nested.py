from finance_quant.dsl.ir import Field, Rolling, to_dict, from_dict


def test_round_trip_preserves_nested_rolling():
    expr = Rolling("std", Rolling("mean", Field("close"), 3), 5)
    assert from_dict(to_dict(expr)) == expr
