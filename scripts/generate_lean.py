"""Generate a LEAN algorithm skeleton from a strategy manifest."""
from __future__ import annotations

import argparse
import re
import sys

from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm
from finance_quant.execution.write import write_algorithm


def _is_hex64(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a LEAN algorithm skeleton")
    parser.add_argument("--strategy-id", default="skeleton")
    parser.add_argument("--dataset-hash", default="0" * 64)
    parser.add_argument("--signal-hash", default="0" * 64)
    parser.add_argument("--symbols", default="SPY")
    parser.add_argument("--out", default="LeanGeneratedAlgorithm.py")
    parser.add_argument("--check", action="store_true",
                        help="verify generated file contains manifest hashes and exit 0/1")
    args = parser.parse_args(argv)

    for name, value in (("dataset-hash", args.dataset_hash), ("signal-hash", args.signal_hash)):
        if not _is_hex64(value):
            print(f"{name} must be a 64-character hex string", file=sys.stderr)
            return 2

    manifest = StrategyManifest(
        strategy_id=args.strategy_id,
        dataset_manifest_hash=args.dataset_hash,
        signal_artifact_hash=args.signal_hash,
        symbols=tuple(args.symbols.split(",")),
        execution_contract=ExecutionContract(),
    )
    if args.check:
        text = generate_algorithm(manifest)
        required = [
            f"strategy_id={args.strategy_id}",
            f"dataset_manifest_hash={args.dataset_hash}",
            f"signal_artifact_hash={args.signal_hash}",
            f"execution_contract_hash={manifest.execution_contract.hash}",
        ]
        missing = [r for r in required if r not in text]
        if missing:
            print(f"missing: {missing}", file=sys.stderr)
            return 1
        print("OK")
        return 0

    path = write_algorithm(manifest, args.out)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
