from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Field, Rolling


def test_qlib_compiles_max_min_quantile():
    assert compile_expr(Rolling("max", Field("close"), 6)) == "Max($close,6)"
    assert compile_expr(Rolling("min", Field("close"), 6)) == "Min($close,6)"
    assert compile_expr(Rolling("quantile", Field("close"), 6)) == "Quantile($close,6)"
