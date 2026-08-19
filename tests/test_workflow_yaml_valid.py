import pytest

from finance_quant.dsl.ir import Field, Rolling
from finance_quant.dsl.workflow import workflow_yaml

yaml = pytest.importorskip("yaml")


def test_workflow_yaml_is_valid_yaml():
    expr = Rolling("mean", Field("close"), 5)
    yml = workflow_yaml(expr, "feat", "2024-01-02", "2024-03-29")
    parsed = yaml.safe_load(yml)
    assert parsed["qlib_init"]["region"] == "cn"
    assert parsed["task"]["model"]["class"] == "LGBModel"
    assert "Mean($close,5)" in parsed["data_handler_config"]["data_loader"]["kwargs"]["config"]["feature"][0][0]
