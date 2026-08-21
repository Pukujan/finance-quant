"""Orchestrate the complete, credential-free Phase B benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Make ``python scripts/run_phase_b_benchmark.py`` behave like module execution.
if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import freeze_fixture, run_b1_b5_phase_b, run_lean_phase_b, run_qlib_phase_b


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = ROOT / "data" / "fixtures" / "phase-b"
DEFAULT_REPORT_DIR = ROOT / "reports"
REPORT_PATH = DEFAULT_REPORT_DIR / "phase_b_benchmark.json"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _freeze_or_load(fixture_dir: Path, freeze: bool) -> tuple[dict[str, Any], str]:
    fixture_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = fixture_dir / freeze_fixture.MANIFEST_NAME
    if freeze or not manifest_path.exists():
        freeze_fixture.main(["--fixture-dir", str(fixture_dir)])
    else:
        freeze_fixture.main(["--fixture-dir", str(fixture_dir), "--verify"])
    return _read_json(manifest_path), _file_hash(manifest_path)


def _run_b1_b5(report_dir: Path) -> tuple[dict[str, Any], list[str]]:
    """Run the fixed-path B1-B5 runner while redirecting its two outputs."""
    # The legacy runner stores a ROOT-relative ledger path in its report, so
    # keep its intermediate artifacts under the repository reports directory.
    intermediate_dir = ROOT / "reports" / "phase_b_benchmark"
    report_path = intermediate_dir / "b1_b5_rank_ic.json"
    ledger_path = intermediate_dir / "experiment_ledger_receipts.jsonl"
    old_report, old_ledger = run_b1_b5_phase_b.REPORT_PATH, run_b1_b5_phase_b.RECEIPT_PATH
    run_b1_b5_phase_b.REPORT_PATH, run_b1_b5_phase_b.RECEIPT_PATH = report_path, ledger_path
    try:
        if run_b1_b5_phase_b.main() != 0:
            raise RuntimeError("B1-B5 runner failed")
    finally:
        run_b1_b5_phase_b.REPORT_PATH, run_b1_b5_phase_b.RECEIPT_PATH = old_report, old_ledger
    receipts = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]
    return _read_json(report_path), [_json_hash(receipt) for receipt in receipts]


def _run_qlib(manifest_path: Path, report_dir: Path) -> tuple[dict[str, Any], str]:
    out_dir = report_dir / "qlib_phase_b"
    if run_qlib_phase_b.main(["--fixture-manifest", str(manifest_path), "--out-dir", str(out_dir)]) != 0:
        raise RuntimeError("Qlib runner failed")
    ledger = out_dir / "experiment_ledger_receipts.jsonl"
    receipt = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
    return _read_json(out_dir / "mlflow_run.json"), _json_hash(receipt)


def _run_lean(b1_report: dict[str, Any], report_dir: Path) -> tuple[dict[str, Any], str]:
    signals_path = report_dir / "phase_b_signals.json"
    signals = {f"B{i}": [run] for i, run in enumerate(b1_report.get("runs", []), start=1)}
    signals_path.write_text(json.dumps({"signals": signals}, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path = report_dir / "lean_phase_b_receipt.json"
    if run_lean_phase_b.main(["--signals", str(signals_path), "--out", str(receipt_path)]) != 0:
        raise RuntimeError("LEAN runner failed")
    receipt = _read_json(receipt_path)
    return receipt, _file_hash(receipt_path)


def run_benchmark(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
    report_path: Path = REPORT_PATH,
    freeze: bool = False,
) -> dict[str, Any]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    fixture, fixture_hash = _freeze_or_load(fixture_dir, freeze)
    b1_report, b1_receipt_hashes = _run_b1_b5(report_path.parent)
    qlib_run, qlib_receipt_hash = _run_qlib(fixture_dir / freeze_fixture.MANIFEST_NAME, report_path.parent)
    lean_receipt, lean_receipt_hash = _run_lean(b1_report, report_path.parent)
    report = {
        "campaign": "phase-b-benchmark",
        "phase": "B",
        "status": "success",
        "fixture": fixture,
        "receipt_hashes": {
            "fixture_manifest": fixture_hash,
            "b1_b5": b1_receipt_hashes,
            "qlib": qlib_receipt_hash,
            "lean": lean_receipt_hash,
        },
        "b1_b5": b1_report,
        "qlib": qlib_run,
        "lean": lean_receipt,
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the complete Phase B benchmark")
    parser.add_argument("--fixture-dir", type=Path, default=DEFAULT_FIXTURE_DIR)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--freeze", action="store_true", help="rebuild the fixture instead of verifying it")
    args = parser.parse_args(argv)
    print(json.dumps(run_benchmark(args.fixture_dir, args.report, args.freeze), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
