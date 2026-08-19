from finance_quant.dsl.ir import Field, Rolling
from finance_quant.dsl.workflow import workflow_yaml


def test_qlib_workflow_yaml_embeds_compiled_expression():
    yaml = workflow_yaml(Rolling("mean", Field("close"), 3), "B1-sma3", "2024-01-01", "2024-03-01")
    assert "Mean($close,3)" in yaml
    assert "LGBModel" in yaml
    assert "2024-01-01" in yaml
