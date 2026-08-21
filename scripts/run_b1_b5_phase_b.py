"""Run deterministic B1-B5 strategies through native WorkOrder stubs.

This is executable plumbing for Phase B.  It deliberately uses fixture-shaped
inputs and local stubs rather than importing the production research stack.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "b1_b5_rank_ic.json"
RECEIPT_PATH = ROOT / "reports" / "experiment_ledger_receipts.jsonl"
CANONICAL_MANIFEST = {
    "manifest_id": "canonical-fixture-v0",
    "dataset": "synthetic-bitemporal-equities",
    "symbols": ["AAA", "BBB", "CCC", "DDD"],
    "start": "2024-01-02",
    "n_days": 45,
    "as_of": "2024-03-05",
}


def content_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_canonical_fixture_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load a canonical manifest when supplied, otherwise use the fixed fixture."""
    candidates = [path] if path else [ROOT / "fixtures" / "canonical_fixture_manifest.json"]
    for candidate in candidates:
        if candidate and candidate.is_file():
            loaded = json.loads(candidate.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or loaded.get("manifest_id") != "canonical-fixture-v0":
                raise ValueError("manifest is not the canonical fixture manifest")
            return loaded
    return dict(CANONICAL_MANIFEST)


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    experiment_id: str
    manifest_hash: str
    strategy: str


@dataclass(frozen=True)
class WorkResult:
    work_order_id: str
    experiment_id: str
    status: str
    n_signals: int
    rank_ic: float
    signal_hash: str


class LocalWorkOrderOrchestrator:
    """Native orchestration seam: submit a WorkOrder and return one result."""

    def run(self, order: WorkOrder, manifest: dict[str, Any],
            strategy: Callable[[dict[str, Any]], tuple[int, float]]) -> WorkResult:
        n_signals, rank_ic = strategy(manifest)
        return WorkResult(order.work_order_id, order.experiment_id, "success", n_signals,
                          rank_ic, content_hash({"order": asdict(order), "rank_ic": rank_ic}))


class ExperimentLedger:
    """Small append-only receipt ledger matching the production boundary."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def record(self, order: WorkOrder, result: WorkResult) -> dict[str, Any]:
        receipt = {
            "receipt_type": "ExperimentLedger",
            "run_id": content_hash(asdict(order))[:16],
            "experiment_id": order.experiment_id,
            "work_order_id": order.work_order_id,
            "status": result.status,
            "dataset_manifest_hash": order.manifest_hash,
            "metrics": {"n_signals": result.n_signals, "rank_ic": result.rank_ic},
            "artifacts": {"signal": result.signal_hash},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, sort_keys=True) + "\n")
        return receipt


def _fixture_days(manifest: dict[str, Any]) -> list[date]:
    start = date.fromisoformat(manifest["start"])
    days: list[date] = []
    current = start
    while len(days) < int(manifest["n_days"]):
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def synthetic_prices(manifest: dict[str, Any]) -> pd.DataFrame:
    """Build deterministic close prices without reading external data."""
    days = _fixture_days(manifest)
    symbols = list(manifest["symbols"])
    values = {}
    for symbol_index, symbol in enumerate(symbols):
        base = 80.0 + symbol_index * 7.0
        values[symbol] = [
            base + day_index * (0.08 + symbol_index * 0.015)
            + ((day_index + 1) * (symbol_index + 3) % 9) * 0.11
            for day_index in range(len(days))
        ]
    return pd.DataFrame(values, index=pd.Index(days, name="date"))


def rank_ic(signals: pd.DataFrame, forward_returns: pd.DataFrame) -> float:
    """Return mean cross-sectional Spearman rank IC for aligned DataFrames."""
    values: list[float] = []
    for day in signals.index.intersection(forward_returns.index):
        pair = pd.concat([signals.loc[day], forward_returns.loc[day]], axis=1).dropna()
        if len(pair) < 2:
            continue
        signal_ranks = pair.iloc[:, 0].rank(method="average")
        return_ranks = pair.iloc[:, 1].rank(method="average")
        correlation = signal_ranks.corr(return_ranks)
        if pd.notna(correlation):
            values.append(float(correlation))
    return sum(values) / len(values) if values else 0.0


def strategy_signals(name: str, prices: pd.DataFrame) -> pd.DataFrame:
    """Compute one signal matrix using only prices available at each date."""
    if name == "B1-sma3":
        return prices / prices.rolling(3, min_periods=3).mean() - 1.0
    if name == "B2-walk-forward":
        # Expanding means use observations through t only; no future data leaks.
        return prices / prices.expanding(min_periods=3).mean() - 1.0
    if name == "B3-momentum":
        return prices.pct_change()
    if name == "B4-xs-rank":
        return prices.rank(axis=1, method="average", pct=True)
    if name == "B5-buy-hold":
        return prices.iloc[0].reindex(prices.columns).to_frame().T.reindex(prices.index).ffill()
    raise ValueError(f"unknown strategy: {name}")


def compute_strategy(name: str, manifest: dict[str, Any]) -> tuple[int, float]:
    """Compute signal count and rank IC for a named B1-B5 baseline."""
    prices = synthetic_prices(manifest)
    signals = strategy_signals(name, prices)
    forward_returns = prices.shift(-1).div(prices).sub(1.0)
    usable = signals.notna() & forward_returns.notna()
    return int(usable.sum().sum()), rank_ic(signals, forward_returns)


# Kept as a narrow import compatibility alias for callers of the old runner API.
strategy_stub = compute_strategy


def main() -> int:
    manifest = load_canonical_fixture_manifest()
    manifest_hash = content_hash(manifest)
    days = _fixture_days(manifest)
    orchestrator = LocalWorkOrderOrchestrator()
    ledger = ExperimentLedger(RECEIPT_PATH)
    runs: list[dict[str, Any]] = []
    for index, experiment_id in enumerate(("B1-sma3", "B2-walk-forward", "B3-momentum",
                                            "B4-xs-rank", "B5-buy-hold"), start=1):
        order = WorkOrder(f"wo-b1b5-{index}", experiment_id, manifest_hash, experiment_id)
        result = orchestrator.run(order, manifest,
                                  lambda fixture, name=experiment_id: compute_strategy(name, fixture))
        receipt = ledger.record(order, result)
        runs.append({"experiment_id": experiment_id, "run_id": receipt["run_id"],
                     "n_signals": result.n_signals, "rank_ic": result.rank_ic})

    report = {"campaign": "B1-B5", "phase": "B", "manifest": manifest,
              "manifest_hash": manifest_hash, "n_days": len(days), "runs": runs,
              "ledger_receipts": str(RECEIPT_PATH.relative_to(ROOT))}
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
