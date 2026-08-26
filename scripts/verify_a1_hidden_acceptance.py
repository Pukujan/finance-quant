"""Verify an aggregate-only A1 hidden-acceptance receipt.

The command consumes only a public seal commitment and a safe aggregate receipt.
It must never be pointed at sealed case or label material.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from finance_quant.acceptance.a1_hidden import (
    A1HiddenAcceptanceError,
    load_safe_receipt,
    load_seal_record,
    verify_a1_hidden_acceptance,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seal-record", required=True)
    parser.add_argument("--safe-receipt", required=True)
    parser.add_argument("--candidate-artifact-hash", required=True)
    args = parser.parse_args()

    try:
        record = load_seal_record(args.seal_record)
        receipt = load_safe_receipt(args.safe_receipt)
        verified = verify_a1_hidden_acceptance(
            record,
            receipt,
            expected_candidate_artifact_hash=args.candidate_artifact_hash,
        )
    except (A1HiddenAcceptanceError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "authority": "NONE", "reason": str(exc)}, sort_keys=True))
        return 2

    print(
        json.dumps(
            {
                "status": "PASS",
                "authority": "NONE",
                "case_set_id": verified.case_set_id,
                "commitment_hash": verified.commitment_hash,
                "candidate_artifact_hash": verified.candidate_artifact_hash,
                "use_number": verified.use_number,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
