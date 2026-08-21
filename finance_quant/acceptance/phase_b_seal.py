"""Sealed holdout acceptance: Merkle-rooted seal records with epoch enforcement.

SEAL-A (exploration): At most 2 seals per epoch.
SEAL-B (promotion): Exactly 1 seal per epoch.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SealType(str, Enum):
    SEAL_A = "SEAL-A"
    SEAL_B = "SEAL-B"


class SealError(ValueError):
    """Raised when a seal record fails validation."""


class SealValidationError(SealError):
    """Merkle root or structural validation failed."""


class SealEpochError(SealError):
    """Epoch constraint (SEAL-A/SEAL-B) violated."""


@dataclass(frozen=True)
class SealRecord:
    """Immutable seal binding a Merkle root to an epoch.

    Labels never leave this record; external systems only see ``merkle_root``.
    """
    merkle_root: str
    epoch: int
    seal_type: SealType
    artifact_hash: str = ""
    count_in_epoch: int = 1
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.merkle_root, str) or len(self.merkle_root) != 64:
            raise SealError("merkle_root must be a 64-char hex string")
        if self.epoch < 1:
            raise SealError("epoch must be >= 1")
        if self.count_in_epoch < 1:
            raise SealError("count_in_epoch must be >= 1")


def _is_valid_hex64(value: str) -> bool:
    import re
    return isinstance(value, str) and len(value) == 64 and re.fullmatch(r"[0-9a-fA-F]+", value) is not None


def _check_merkle_root(merkle_root: str, seal_record: SealRecord) -> None:
    if not _is_valid_hex64(merkle_root):
        raise SealValidationError("merkle_root arg is not a valid 64-char hex string")
    if merkle_root != seal_record.merkle_root:
        raise SealValidationError("merkle_root mismatch: record does not match provided root")


def _check_epoch_counts(seal_record: SealRecord, registry: "dict[int, dict[SealType, int]] | None") -> None:
    epoch_counts = registry or {}
    current = epoch_counts.get(seal_record.epoch, {}).get(seal_record.seal_type, 0)
    observed = current + seal_record.count_in_epoch

    if seal_record.seal_type is SealType.SEAL_A:
        if observed > 2:
            raise SealEpochError(
                f"SEAL-A: at most 2 seals per epoch, would have {observed} in epoch {seal_record.epoch}"
            )
    elif seal_record.seal_type is SealType.SEAL_B:
        if observed != 1:
            raise SealEpochError(
                f"SEAL-B: exactly 1 seal per epoch, would have {observed} in epoch {seal_record.epoch}"
            )
    else:
        raise SealError(f"unknown seal_type: {seal_record.seal_type!r}")


def validate(
    merkle_root: str,
    seal_record: SealRecord,
    registry: dict[int, dict[SealType, int]] | None = None,
) -> SealRecord:
    """Validate a seal record: Merkle root + epoch constraints, no labels exposed.

    Args:
        merkle_root: Expected Merkle root (opaque hex string).
        seal_record: The sealed record to validate.
        registry: Optional {epoch: {SealType: count}} for epoch enforcement.

    Returns:
        The same SealRecord on success.

    Raises:
        SealValidationError: Root mismatch or structural failure.
        SealEpochError: SEAL-A >2/epoch or SEAL-B !=1/epoch.
    """
    _check_merkle_root(merkle_root, seal_record)
    _check_epoch_counts(seal_record, registry)
    return seal_record
