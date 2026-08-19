from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Const, Unary


def test_qlib_compiles_const_and_unary():
    assert compile_expr(Const(2.5)) == "2.5"
    assert compile_expr(Unary("neg", Const(1.0))) == "Neg(1.0)"
