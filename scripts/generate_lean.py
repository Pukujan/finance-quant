"""Generate a LEAN algorithm skeleton from a strategy manifest."""
from __future__ import annotations

import argparse
import sys

from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm
from finance_quant.execution.write import write_algorithm


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a LEAN algorithm skeleton")
    parser.add_argument("--strategy-id", default="skeleton")
    parser.add_argument("--dataset-hash", default="0" * 64)
    parser.add_argument("--signal-hash", default="0" * 64)
    parser.add_argument("--symbols", default="SPY")
    parser.add_argument("--out", default="LeanGeneratedAlgorithm.py")
    args = parser.parse_args(argv)

    manifest = StrategyManifest(
        strategy_id=args.strategy_id,
        dataset_manifest_hash=args.dataset_hash,
        signal_artifact_hash=args.signal_hash,
        symbols=tuple(args.symbols.split(",")),
        execution_contract=ExecutionContract(),
    )
    path = write_algorithm(manifest, args.out)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
