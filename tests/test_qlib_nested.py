from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Binary, Field, Lag, Rolling


def test_qlib_compiler_nested_mean_ref():
    expr = Rolling("mean", Lag(Field("close"), 1), 5)
    assert compile_expr(expr) == "Mean(Ref($close,1),5)"
    expr2 = Binary("div", Field("close"), Field("volume"))
    assert compile_expr(expr2) == "Div($close,$volume)"
