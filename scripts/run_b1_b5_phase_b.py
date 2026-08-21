"""Run deterministic B1-B5 strategy stubs through native WorkOrder stubs.

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


def strategy_stub(name: str, manifest: dict[str, Any]) -> tuple[int, float]:
    """Return stable fixture-shaped metrics for a named B1-B5 baseline."""
    values = {
        "B1-sma3": (132, 0.118),
        "B2-walk-forward": (128, 0.104),
        "B3-momentum": (120, 0.091),
        "B4-xs-rank": (116, 0.083),
        "B5-buy-hold": (4, 0.017),
    }
    if name not in values:
        raise ValueError(f"unknown strategy stub: {name}")
    return values[name]


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
                                  lambda fixture, name=experiment_id: strategy_stub(name, fixture))
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
