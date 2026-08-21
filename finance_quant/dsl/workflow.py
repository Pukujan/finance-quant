"""Generate a Qlib workflow YAML from an approved Tier-1 expression. No Qlib import."""
from __future__ import annotations

from .checker import check
from .ir import Binary, CrossSection, Expr, Lag, Rolling, RollingPair, Unary
from .qlib import QlibCompileError, compile_expr


def _contains_cross_section(expr: Expr) -> bool:
    if isinstance(expr, CrossSection):
        return True
    if isinstance(expr, Unary):
        return _contains_cross_section(expr.arg)
    if isinstance(expr, Binary):
        return _contains_cross_section(expr.left) or _contains_cross_section(expr.right)
    if isinstance(expr, (Lag, Rolling)):
        return _contains_cross_section(expr.arg)
    if isinstance(expr, RollingPair):
        return _contains_cross_section(expr.left) or _contains_cross_section(expr.right)
    return False


def workflow_yaml(expr: Expr, experiment_name: str, start: str, end: str) -> str:
    check(expr)
    if _contains_cross_section(expr):
        raise QlibCompileError(
            "cross-sectional expressions require compile_cross_sectional() and "
            "the bitemporal universe-aware handler; they cannot be emitted in a "
            "scalar Qlib workflow"
        )
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
        feature: [[{qlib_expr!r}, '{experiment_name}']]
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
