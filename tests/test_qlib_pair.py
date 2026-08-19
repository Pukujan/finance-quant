from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.ir import Field, RollingPair


def test_qlib_compiles_cov_and_rsquare():
    assert compile_expr(RollingPair("cov", Field("close"), Field("volume"), 5)) == "Cov($close,$volume,5)"
    assert compile_expr(RollingPair("rsquare", Field("close"), Field("volume"), 5)) == "Rsquare($close,$volume,5)"
