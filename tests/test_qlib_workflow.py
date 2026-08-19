from finance_quant.dsl.ir import Field, Rolling
from finance_quant.dsl.qlib import compile_expr
from finance_quant.dsl.workflow import workflow_yaml


def test_rolling_mean_compiles_to_qlib_mean():
    expr = Rolling("mean", Field("close"), 5)
    assert compile_expr(expr) == "Mean($close,5)"


def test_workflow_yaml_contains_expression_and_dates():
    expr = Rolling("mean", Field("close"), 5)
    yml = workflow_yaml(expr, "feat", "2024-01-02", "2024-03-29")
    assert "Mean($close,5)" in yml
    assert "2024-01-02" in yml
    assert "2024-03-29" in yml
    assert "feat" in yml
