"""Public, tamper-evident sealed-case commitment interface.

Exact cases and labels stay in finance-quant-holdout. The public repository keeps
only the commitment record and safe aggregate receipt schema.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def merkle_root(case_hashes: list[str]) -> str:
    """Stable binary Merkle root. Input case hashes are sorted to make ordering irrelevant."""
    level = sorted(case_hashes)
    if not level:
        raise ValueError("sealed suite must contain at least one case")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256((level[i] + level[i + 1]).encode()).hexdigest()
                 for i in range(0, len(level), 2)]
    return level[0]


@dataclass(frozen=True)
class SealRecord:
    case_set_id: str
    case_merkle_root: str
    labels_hash: str
    sealed_at: str
    eval_harness_sha: str
    scorecard_ref: str
    max_uses: int

    @property
    def commitment_hash(self) -> str:
        return _hash(asdict(self))


@dataclass(frozen=True)
class SafeAcceptanceReceipt:
    """Only aggregate evidence that may flow out of the sealed clean runner."""
    case_set_id: str
    commitment_hash: str
    candidate_artifact_hash: str
    status: str                 # pass | fail | invalid
    aggregate_metrics: tuple[tuple[str, float], ...]
    failure_classes: tuple[str, ...]
    use_number: int

    def __post_init__(self) -> None:
        if self.status not in {"pass", "fail", "invalid"}:
            raise ValueError("invalid acceptance status")
        if self.use_number < 1:
            raise ValueError("use number begins at 1")
