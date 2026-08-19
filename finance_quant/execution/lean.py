"""Generated LEAN algorithm skeleton and explicit execution semantics contract."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExecutionContract:
    version: str = "0.1"
    fill_model: str = "EquityFillModel"
    slippage_model: str = "VolumeShareSlippage"
    fee_model: str = "InteractiveBrokersFeeModel"
    adjustment_mode: str = "Raw"
    daily_fill_rule: str = "signal_at_bar_t_fills_no_earlier_than_t_plus_1_open"

    @property
    def hash(self) -> str:
        return hashlib.blake2b(json.dumps(asdict(self), sort_keys=True).encode(), digest_size=32).hexdigest()


@dataclass(frozen=True)
class StrategyManifest:
    strategy_id: str
    dataset_manifest_hash: str
    signal_artifact_hash: str
    symbols: tuple[str, ...]
    execution_contract: ExecutionContract


def generate_algorithm(manifest: StrategyManifest) -> str:
    """Deterministic Python LEAN stub. Hand edits are forbidden: regenerate."""
    return f'''# GENERATED FILE - DO NOT EDIT.
# strategy_id={manifest.strategy_id}
# dataset_manifest_hash={manifest.dataset_manifest_hash}
# signal_artifact_hash={manifest.signal_artifact_hash}
# execution_contract_hash={manifest.execution_contract.hash}
from AlgorithmImports import *

class GeneratedFinanceQuantAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetCash(100000)
        self.SetDataNormalizationMode(DataNormalizationMode.{manifest.execution_contract.adjustment_mode})
        self._symbols = [self.AddEquity(t, Resolution.Daily).Symbol for t in {list(manifest.symbols)!r}]
        # Contract: signal at bar t cannot fill earlier than next-bar open.
        # Inputs come from the manifest-pinned extract, never QC cloud data.

    def OnData(self, data):
        pass
'''
