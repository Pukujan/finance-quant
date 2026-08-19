from finance_quant.dsl.qlib import QlibCompileError, compile_expr
from finance_quant.dsl.ir import Field, Lag
import pytest


def test_qlib_compiler_rejects_leaky_ir_before_emit():
    with pytest.raises(Exception):
        compile_expr(Lag(Field("close"), -1))
