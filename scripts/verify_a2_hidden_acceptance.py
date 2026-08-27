"""Verify aggregate-only A2 hidden acceptance without reading hidden material."""
from __future__ import annotations

import argparse
import json

from finance_quant.acceptance.a2_hidden import (
    A2HiddenAcceptanceError,
    load_a2_safe_receipt,
    load_a2_seal_record,
    verify_a2_hidden_acceptance,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seal-record", required=True)
    parser.add_argument("--safe-receipt", required=True)
    parser.add_argument("--candidate-artifact-hash", required=True)
    parser.add_argument("--public-eval-sha", required=True)
    args = parser.parse_args()
    try:
        record = load_a2_seal_record(args.seal_record)
        receipt = load_a2_safe_receipt(args.safe_receipt)
        verified = verify_a2_hidden_acceptance(
            record,
            receipt,
            expected_candidate_artifact_hash=args.candidate_artifact_hash,
            expected_public_eval_sha=args.public_eval_sha,
        )
    except (A2HiddenAcceptanceError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "authority": "NONE", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps({
        "status": "PASS",
        "authority": "NONE",
        "case_set_id": verified.case_set_id,
        "commitment_hash": verified.commitment_hash,
        "candidate_artifact_hash": verified.candidate_artifact_hash,
        "use_number": verified.use_number,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
