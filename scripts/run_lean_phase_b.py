"""Run a deterministic, credential-free LEAN Phase B replay stub.

This is plumbing for B1-B5 signals, not a live LEAN integration.  The child
process stands in for LEAN so that receipts preserve the subprocess boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


MODELS = {
    "fill": "ImmediateSameBarFillModel",
    "slippage": "ConstantSlippageModel",
    "fee": "ZeroFeeModel",
}


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _load_signals(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {name: [] for name in ("B1", "B2", "B3", "B4", "B5")}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("signals must be a JSON object")
    signals = data.get("signals", data)
    if not isinstance(signals, dict):
        raise ValueError("signals must be a JSON object or {\"signals\": {...}}")
    return {name: signals.get(name, []) for name in ("B1", "B2", "B3", "B4", "B5")}


def build_custom_data_source(signals: dict[str, Any]) -> str:
    """Return the generated Python source for a minimal LEAN custom source."""
    encoded = json.dumps(signals, sort_keys=True, separators=(",", ":"))
    return f'''# Generated Phase B custom data source stub.\n# No market data or live LEAN dependency is used.\nclass PhaseBSignalData:\n    SYMBOL = "PHASE_B_SIGNAL"\n    SIGNALS = {encoded}\n\n    def get_source(self):\n        return self.SIGNALS\n\n    def reader(self, row):\n        return row\n'''


def _child_code() -> str:
    return (
        "import json,sys; request=json.load(sys.stdin); "
        "print(json.dumps({'engine':'lean-subprocess-stub','status':'success',"
        "'signal_count':sum(len(v) for v in request['signals'].values()),"
        "'slippage_bps':request['slippage_bps']}))"
    )


def run_variant(signals: dict[str, Any], slippage_bps: float, default_slippage_bps: float) -> dict[str, Any]:
    request = {"signals": signals, "slippage_bps": slippage_bps}
    completed = subprocess.run(
        [sys.executable, "-c", _child_code()],
        input=json.dumps(request), text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "LEAN subprocess stub failed")
    result = json.loads(completed.stdout)
    result["variant"] = "2x_slippage" if slippage_bps > default_slippage_bps else "nominal"
    result["models"] = dict(MODELS)
    result["slippage_bps"] = slippage_bps
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Phase B LEAN replay stub")
    parser.add_argument("--signals", type=Path, help="JSON file containing B1-B5 signals")
    parser.add_argument("--out", type=Path, default=Path("lean_phase_b_receipt.json"))
    parser.add_argument("--strategy-id", default="phase-b-baselines")
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    args = parser.parse_args(argv)

    signals = _load_signals(args.signals)
    source = build_custom_data_source(signals)
    source_path = args.out.with_name(args.out.stem + "_custom_data.py")
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(source, encoding="utf-8")
    nominal = run_variant(signals, args.slippage_bps, args.slippage_bps)
    stressed = run_variant(signals, args.slippage_bps * 2, args.slippage_bps)
    receipt = {
        "strategy_id": args.strategy_id,
        "status": "success",
        "engine": "lean-subprocess-stub",
        "signals": signals,
        "signal_hash": _hash(signals),
        "custom_data_source": str(source_path),
        "models": dict(MODELS),
        "cost_stress": {"nominal": nominal, "2x_slippage": stressed},
        "todo": ["Replace subprocess stub with pinned LEAN invocation", "Add real B1-B5 performance metrics"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
