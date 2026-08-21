"""Compare nominal and 2x-slippage LEAN Phase B replays.

The LEAN runner is intentionally a small, credential-free seam.  This report
keeps the cost comparison here so that callers can replace the runner (or a
real LEAN adapter) without changing the report contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import run_lean_phase_b


DEFAULT_SLIPPAGE_BPS = 5.0
STRATEGIES = ("B1", "B2", "B3", "B4", "B5")


def _hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _signals(path: Path) -> dict[str, list[Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("signals must be a JSON object")
    value = value.get("signals", value)
    if not isinstance(value, dict):
        raise ValueError("signals must be a JSON object or {\"signals\": {...}}")
    return {name: list(value.get(name, [])) for name in STRATEGIES}


def _number(item: Any, *names: str, default: float = 0.0) -> float:
    if isinstance(item, dict):
        for name in names:
            if isinstance(item.get(name), (int, float)):
                return float(item[name])
    return default


def _returns(items: Iterable[Any], result: dict[str, Any], name: str) -> list[float]:
    strategies = result.get("strategies", {})
    item = strategies.get(name, {}) if isinstance(strategies, dict) else {}
    values = item.get("returns") if isinstance(item, dict) else None
    if isinstance(values, list):
        return [float(value) for value in values if isinstance(value, (int, float))]
    return [
        _number(value, "return", "pnl", "daily_return", default=0.0)
        for value in items
        if isinstance(value, dict)
    ]


def _drawdown(returns: list[float]) -> float:
    equity = peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = max(worst, (peak - equity) / peak)
    return worst


def _metrics(name: str, items: list[Any], result: dict[str, Any], slippage_bps: float) -> dict[str, float | int]:
    strategies = result.get("strategies", {})
    supplied = strategies.get(name, {}) if isinstance(strategies, dict) else {}
    returns = _returns(items, result, name)
    gross = _number(supplied, "gross_return", "return", "total_return", default=sum(returns))
    turnover = _number(supplied, "turnover", default=sum(
        _number(item, "turnover", "notional_turnover", default=1.0) for item in items
    ))
    total_return = gross - turnover * slippage_bps / 10_000.0
    if isinstance(supplied, dict) and isinstance(supplied.get("total_return"), (int, float)):
        total_return = float(supplied["total_return"]) - turnover * slippage_bps / 10_000.0
    adjusted = returns[:]
    if adjusted:
        adjusted[-1] -= turnover * slippage_bps / 10_000.0
    mean = sum(adjusted) / len(adjusted) if adjusted else 0.0
    variance = sum((value - mean) ** 2 for value in adjusted) / len(adjusted) if adjusted else 0.0
    sharpe = mean / math.sqrt(variance) * math.sqrt(len(adjusted)) if variance else 0.0
    return {"signal_count": len(items), "total_return": total_return,
            "sharpe_approximation": sharpe, "max_drawdown": _drawdown(adjusted),
            "turnover": turnover}


def compare(signals: dict[str, list[Any]], nominal_bps: float = DEFAULT_SLIPPAGE_BPS) -> dict[str, Any]:
    variants = {}
    for label, bps in (("nominal", nominal_bps), ("2x_slippage", nominal_bps * 2)):
        result = run_lean_phase_b.run_variant(signals, bps, nominal_bps)
        variants[label] = {"cost_model": f"constant-slippage-{bps:g}bps",
                           "slippage_bps": bps, "receipt_hash": _hash(result),
                           "result": result,
                           "strategies": {name: _metrics(name, signals[name], result, bps)
                                          for name in STRATEGIES}}
        variants[label]["aggregate"] = _aggregate(variants[label]["strategies"])
    ok = _monotonic(variants["nominal"], variants["2x_slippage"])
    return {"status": "success", "cost_models": variants,
            "monotonic_degradation_ok": ok}


def _aggregate(metrics: dict[str, dict[str, float | int]]) -> dict[str, float | int]:
    total = sum(float(value["total_return"]) for value in metrics.values())
    turnover = sum(float(value["turnover"]) for value in metrics.values())
    count = sum(int(value["signal_count"]) for value in metrics.values())
    drawdown = max((float(value["max_drawdown"]) for value in metrics.values()), default=0.0)
    sharpes = [float(value["sharpe_approximation"]) for value in metrics.values()]
    return {"signal_count": count, "total_return": total,
            "sharpe_approximation": sum(sharpes) / len(sharpes) if sharpes else 0.0,
            "max_drawdown": drawdown, "turnover": turnover}


def _monotonic(nominal: dict[str, Any], stressed: dict[str, Any]) -> bool:
    for name in (*STRATEGIES, "aggregate"):
        before, after = nominal["strategies"].get(name, nominal["aggregate"]), stressed["strategies"].get(name, stressed["aggregate"])
        if after["total_return"] > before["total_return"] or after["max_drawdown"] < before["max_drawdown"]:
            return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report Phase B cost stress")
    parser.add_argument("--signals", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("reports/cost_stress.json"))
    parser.add_argument("--slippage-bps", type=float, default=DEFAULT_SLIPPAGE_BPS)
    args = parser.parse_args(argv)
    report = compare(_signals(args.signals), args.slippage_bps)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0 if report["monotonic_degradation_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
