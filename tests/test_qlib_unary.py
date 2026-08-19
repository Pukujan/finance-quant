from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Field, Unary


def test_qlib_compiles_abs_log_sign():
    assert compile_expr(Unary("abs", Field("close"))) == "Abs($close)"
    assert compile_expr(Unary("log", Field("close"))) == "Log($close)"
    assert compile_expr(Unary("sign", Field("close"))) == "Sign($close)"
