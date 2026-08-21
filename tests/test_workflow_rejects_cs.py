import pytest

from finance_quant.dsl.ir import CrossSection, Field
from finance_quant.dsl.qlib import QlibCompileError
from finance_quant.dsl.workflow import workflow_yaml


def test_workflow_yaml_rejects_cross_sectional_ir_with_handler_guidance():
    expr = CrossSection("rank", Field("close"), "FIXIDX")

    with pytest.raises(QlibCompileError, match="compile_cross_sectional"):
        workflow_yaml(expr, "cs-rank", "2024-01-01", "2024-03-01")
