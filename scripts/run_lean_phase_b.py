"""Run a deterministic, credential-free LEAN Phase B replay stub.

This is plumbing for B1-B5 signals, not a live LEAN integration.  The child
process stands in for LEAN so that receipts preserve the subprocess boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
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


def detect_lean_cli(search_dir: Path | None = None) -> str | None:
    """Return a usable local LEAN executable, if one is configured or on PATH."""
    search_dir = search_dir or Path.cwd()
    configured = search_dir / "lean.json"
    executable: str | None = None
    if configured.is_file():
        try:
            config = json.loads(configured.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            config = {}
        if isinstance(config, dict):
            value = config.get("executable") or config.get("lean_cli") or config.get("lean")
            if isinstance(value, str) and value:
                candidate = Path(value)
                if not candidate.is_absolute():
                    candidate = search_dir / candidate
                if candidate.is_file():
                    executable = str(candidate)
    return executable or shutil.which("lean")


def _run_lean_backtest(
    signals: dict[str, Any], slippage_bps: float, lean_cli: str,
) -> dict[str, Any]:
    """Run LEAN in a disposable project containing the generated data source."""
    with tempfile.TemporaryDirectory(prefix="lean-phase-b-") as directory:
        project = Path(directory)
        (project / "lean.json").write_text("{}\n", encoding="utf-8")
        (project / "PhaseBSignalData.py").write_text(
            build_custom_data_source(signals), encoding="utf-8"
        )
        # The generated algorithm is deliberately minimal: the CLI invocation is
        # the integration boundary; data-source semantics remain credential-free.
        (project / "main.py").write_text(
            "class PhaseBAlgorithm:\n    pass\n", encoding="utf-8"
        )
        completed = subprocess.run(
            [lean_cli, "backtest"],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "LEAN backtest failed")
    return {
        "engine": "lean-cli",
        "status": "success",
        "slippage_bps": slippage_bps,
        "output": completed.stdout.strip(),
    }


def run_variant(
    signals: dict[str, Any], slippage_bps: float, default_slippage_bps: float,
    lean_cli: str | None = None,
) -> dict[str, Any]:
    if lean_cli:
        result = _run_lean_backtest(signals, slippage_bps, lean_cli)
    else:
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
    lean_cli = detect_lean_cli()
    nominal = run_variant(signals, args.slippage_bps, args.slippage_bps, lean_cli)
    stressed = run_variant(signals, args.slippage_bps * 2, args.slippage_bps, lean_cli)
    engine = "lean-cli" if lean_cli else "lean-subprocess-stub"
    receipt = {
        "strategy_id": args.strategy_id,
        "status": "success",
        "engine": engine,
        "signals": signals,
        "signal_hash": _hash(signals),
        "custom_data_source": str(source_path),
        "models": dict(MODELS),
        "cost_stress": {"nominal": nominal, "2x_slippage": stressed},
        "todo": ["Pin the LEAN CLI/data environment", "Add real B1-B5 performance metrics"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
