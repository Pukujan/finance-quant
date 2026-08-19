from finance_quant.dsl.ir import Const, to_dict
from finance_quant.orchestration.contracts import content_hash


def test_const_canonical_hash_depends_on_value():
    assert content_hash(to_dict(Const(1.0))) != content_hash(to_dict(Const(2.0)))
    assert content_hash(to_dict(Const(1.0))) == content_hash(to_dict(Const(1.0)))
