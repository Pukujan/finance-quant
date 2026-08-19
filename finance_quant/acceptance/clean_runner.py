"""Clean-runner shaped scoring: public hashes in, aggregate receipt out. No case payloads."""
from __future__ import annotations

import json
from pathlib import Path

from finance_quant.acceptance.mini_set import make_mini_set_commitment, write_mini_set_receipt
from finance_quant.acceptance.uses import assert_use_allowed
from finance_quant.orchestration.contracts import content_hash


def score_public_mini_set(candidate_artifact_hash: str, case_hashes: list[str],
                          labels_hash: str, metrics: dict[str, float],
                          failure_classes: list[str], out: Path) -> Path:
    seal = make_mini_set_commitment(case_hashes, labels_hash, "h" * 40, max_uses=2)
    assert_use_allowed(seal, 1)
    return write_mini_set_receipt(seal, candidate_artifact_hash, metrics, failure_classes, out)
