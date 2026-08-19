from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Binary, Const, Field


def test_qlib_min_max_compile():
    assert compile_expr(Binary("min", Field("close"), Const(1.0))) == "Min($close,1.0)"
    assert compile_expr(Binary("max", Field("close"), Const(1.0))) == "Max($close,1.0)"
