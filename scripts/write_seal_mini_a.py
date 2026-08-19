"""Write a public SEAL-MINI-A commitment from case hashes only (no payloads)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.acceptance.mini_set import make_mini_set_commitment, write_mini_set_receipt
from finance_quant.orchestration.contracts import content_hash


import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write SEAL-MINI-A public commitment")
    parser.add_argument("--out", default="docs/acceptance/SEAL_MINI_A.json")
    args = parser.parse_args(argv)

    # Synthetic public hashes only. Real cases live in finance-quant-holdout.
    case_hashes = [content_hash(f"mini-case-{i}") for i in range(8)]
    labels_hash = content_hash("labels-not-in-this-repo")
    seal = make_mini_set_commitment(case_hashes, labels_hash, "h" * 40, max_uses=2)
    out = Path(args.out)
    write_mini_set_receipt(seal, "no-candidate-yet", {}, [], out)
    print(json.dumps({
        "path": str(out),
        "case_set_id": seal.case_set_id,
        "commitment_hash": seal.commitment_hash,
        "max_uses": seal.max_uses,
        "n_cases": len(case_hashes),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
