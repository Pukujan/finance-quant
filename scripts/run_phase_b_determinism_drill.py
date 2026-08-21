"""Run the Phase B benchmark N times and compare receipt hashes for determinism.

Usage::

    python scripts/run_phase_b_determinism_drill.py --runs 3 --fixture-dir data/fixtures/phase-b

Returns 0 when every run produces identical hashes; 1 on any mismatch.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

# Make scripts importable when run as a top-level module.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import run_b1_b5_phase_b as b1b5
from scripts import run_lean_phase_b as lean
from scripts import run_qlib_phase_b as qlib
from scripts.freeze_fixture import canonical_json, compute_manifest_hash, load_store


def content_hash(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def run_fixture_hash(fixture_dir: Path) -> str:
    """Return the canonical manifest hash for the fixture directory."""
    manifest_path = fixture_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        store = load_store(None)
        records = store.dump_records()
        manifest = {"records": records}
    return compute_manifest_hash(manifest.get("records", [])) if "records" in manifest else content_hash(manifest)


def run_b1_b5_receipt_hash(fixture_dir: Path, work_dir: Path) -> dict[str, str]:
    """Run B1-B5 benchmark and return per-experiment receipt hashes."""
    old_receipt = b1b5.RECEIPT_PATH
    old_report = b1b5.REPORT_PATH
    b1b5.RECEIPT_PATH = work_dir / "experiment_ledger_receipts.jsonl"
    b1b5.REPORT_PATH = work_dir / "b1_b5_rank_ic.json"
    try:
        b1b5.main()
        lines = b1b5.RECEIPT_PATH.read_text(encoding="utf-8").strip().splitlines()
        return {json.loads(line)["run_id"]: content_hash(json.loads(line)) for line in lines}
    finally:
        b1b5.RECEIPT_PATH = old_receipt
        b1b5.REPORT_PATH = old_report


def run_qlib_receipt_hash(fixture_dir: Path, work_dir: Path) -> str:
    """Run Qlib Phase B and return the mlflow run hash."""
    out_dir = work_dir / "qlib_out"
    manifest_path = fixture_dir / "manifest.json"
    qlib.main(["--fixture-manifest", str(manifest_path), "--out-dir", str(out_dir)])
    mlflow_path = out_dir / "mlflow_run.json"
    return content_hash(json.loads(mlflow_path.read_text(encoding="utf-8")))


def run_lean_receipt_hash(fixture_dir: Path, work_dir: Path) -> str:
    """Run LEAN Phase B stub and return the receipt hash."""
    out_path = work_dir / "lean_receipt.json"
    lean.main(["--out", str(out_path)])
    return content_hash(json.loads(out_path.read_text(encoding="utf-8")))


def run_one_iteration(run_index: int, fixture_dir: Path, work_dir: Path) -> dict[str, Any]:
    """Execute all Phase B runners once and collect hashes."""
    return {
        "run_index": run_index,
        "fixture_hash": run_fixture_hash(fixture_dir),
        "b1_b5_receipts": run_b1_b5_receipt_hash(fixture_dir, work_dir / f"b1b5_{run_index}"),
        "qlib_receipt": run_qlib_receipt_hash(fixture_dir, work_dir / f"qlib_{run_index}"),
        "lean_receipt": run_lean_receipt_hash(fixture_dir, work_dir / f"lean_{run_index}"),
    }


def hashes_match(all_results: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Compare hashes across runs. Return (all_match, mismatches)."""
    mismatches: list[str] = []
    reference = all_results[0]

    for key in ("fixture_hash", "qlib_receipt", "lean_receipt"):
        ref_value = reference[key]
        for idx, result in enumerate(all_results[1:], start=1):
            if result[key] != ref_value:
                mismatches.append(f"{key} run 0 vs run {idx}: {ref_value} != {result[key]}")

    ref_b1b5 = reference["b1_b5_receipts"]
    for idx, result in enumerate(all_results[1:], start=1):
        cur_b1b5 = result["b1_b5_receipts"]
        if set(ref_b1b5.keys()) != set(cur_b1b5.keys()):
            mismatches.append(f"b1_b5_receipts keys differ run 0 vs run {idx}")
        else:
            for run_id in ref_b1b5:
                if ref_b1b5[run_id] != cur_b1b5[run_id]:
                    mismatches.append(f"b1_b5_receipts[{run_id}] run 0 vs run {idx} mismatch")

    return len(mismatches) == 0, mismatches


def run_benchmark(n_runs: int = 3, fixture_dir: Path | None = None) -> tuple[bool, list[dict[str, Any]], list[str]]:
    """Run Phase B benchmark *n_runs* times and check determinism.

    Returns (all_match, all_results, mismatches).
    """
    if fixture_dir is None:
        fixture_dir = Path("data/fixtures/phase-b")

    with tempfile.TemporaryDirectory(prefix="phase-b-drill-") as tmp:
        work_dir = Path(tmp)
        all_results = []
        for i in range(n_runs):
            print(f"--- Run {i}/{n_runs - 1} ---")
            result = run_one_iteration(i, fixture_dir, work_dir)
            all_results.append(result)

    all_match, mismatches = hashes_match(all_results)
    return all_match, all_results, mismatches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase B determinism drill")
    parser.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument("--fixture-dir", type=Path, default=Path("data/fixtures/phase-b"))
    args = parser.parse_args(argv)

    all_match, all_results, mismatches = run_benchmark(n_runs=args.runs, fixture_dir=args.fixture_dir)

    for idx, result in enumerate(all_results):
        print(f"Run {idx}: fixture={result['fixture_hash'][:16]}... "
              f"b1b5={len(result['b1_b5_receipts'])} receipts "
              f"qlib={result['qlib_receipt'][:16]}... "
              f"lean={result['lean_receipt'][:16]}...")

    if all_match:
        print(f"DETERMINISM OK: all {args.runs} runs produced identical hashes")
        return 0
    else:
        print("DETERMINISM FAILED:")
        for msg in mismatches:
            print(f"  - {msg}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
