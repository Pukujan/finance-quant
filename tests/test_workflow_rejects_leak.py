from finance_quant.dsl.workflow import workflow_yaml
from finance_quant.dsl.ir import Field, Lag
import pytest


def test_workflow_yaml_refuses_leaky_ir():
    with pytest.raises(Exception):
        workflow_yaml(Lag(Field("close"), -1), "leak", "2024-01-01", "2024-02-01")
