"""Generate a Qlib workflow YAML from an approved Tier-1 expression. No Qlib import."""
from __future__ import annotations

from .checker import check
from .ir import Expr
from .qlib import compile_expr


def workflow_yaml(expr: Expr, experiment_name: str, start: str, end: str) -> str:
    check(expr)
    qlib_expr = compile_expr(expr)
    return f"""qlib_init:
  provider_uri: ~/.qlib/qlib_data/cn_data
  region: cn
market: &market {{start_time: '{start}', end_time: '{end}'}}
data_handler_config: &data_handler_config
  start_time: '{start}'
  end_time: '{end}'
  instruments: *market
  data_loader:
    class: QlibDataLoader
    kwargs:
      config:
        feature: [[{qlib_expr}, '{experiment_name}']]
task:
  model:
    class: LGBModel
    module_path: qlib.contrib.model.gbdt
  dataset:
    class: DatasetH
    module_path: qlib.data.dataset
    kwargs:
      handler:
        class: DataHandlerLP
        module_path: qlib.contrib.data.handler
        kwargs: *data_handler_config
"""
