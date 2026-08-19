from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Field, Rolling


def test_qlib_compiles_sum_std_rank():
    assert compile_expr(Rolling("sum", Field("close"), 4)) == "Sum($close,4)"
    assert compile_expr(Rolling("std", Field("close"), 4)) == "Std($close,4)"
    assert compile_expr(Rolling("rank", Field("close"), 4)) == "Rank($close,4)"
