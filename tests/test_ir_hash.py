from finance_quant.dsl.ir import Field, Rolling, to_dict
from finance_quant.orchestration.contracts import content_hash


def test_ir_canonical_hash_is_stable():
    expr = Rolling("mean", Field("close"), 3)
    assert content_hash(to_dict(expr)) == content_hash(to_dict(expr))
    assert content_hash(to_dict(expr)) != content_hash(to_dict(Rolling("mean", Field("close"), 4)))
