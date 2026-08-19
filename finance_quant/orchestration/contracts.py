"""WorkOrder / ResultReceipt contracts and content-addressed hashing.

Design (docs/spikes/10): attempt_id == work_order_hash == content address of the
canonical WorkOrder. A retry of an identical WorkOrder is therefore structurally
idempotent: it names the same row rather than creating parallel truth.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Tuple


class ContractError(ValueError):
    """A contract violation: malformed, semantically invalid, or unauthorized."""


class AuthorityClass(str, Enum):
    RESEARCH_WORKER = "research_worker"
    SEALED_SCORING = "sealed_scoring"


class EgressClass(str, Enum):
    NONE = "none"
    LITELLM_ONLY = "litellm_only"
    VENDOR_DATA_ONLY = "vendor_data_only"


def _default(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (tuple, frozenset)):
        return sorted(obj) if isinstance(obj, frozenset) else list(obj)
    raise ContractError(f"not canonicalizable: {type(obj)!r}")


def canonical_json(obj: Any) -> bytes:
    """Deterministic canonical encoding: sorted keys, tight separators."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_default
    ).encode("utf-8")


def content_hash(obj: Any) -> str:
    return hashlib.blake2b(canonical_json(obj), digest_size=32).hexdigest()


@dataclass(frozen=True)
class ResourceRequest:
    cpu: int = 1
    mem_mb: int = 512
    wall_timeout_s: float = 60.0
    heartbeat_s: float = 2.0

    def __post_init__(self) -> None:
        if self.cpu < 1 or self.mem_mb < 1:
            raise ContractError("resource request must be positive")
        if self.wall_timeout_s <= 0 or self.heartbeat_s <= 0:
            raise ContractError("timeouts must be positive")
        if self.heartbeat_s >= self.wall_timeout_s:
            raise ContractError("heartbeat interval must be < wall timeout")


@dataclass(frozen=True)
class Artifact:
    ref: str
    sha256: str
    bytes: int


@dataclass(frozen=True)
class WorkOrder:
    """Immutable once issued. attempt_id is the content hash."""

    campaign_id: str
    task_type: str
    dataset_snapshot_id: str
    code_commit: str
    seeds: Tuple[int, ...]
    manifest_hash: str
    resource_request: ResourceRequest = field(default_factory=ResourceRequest)
    factor_hash: Optional[str] = None
    model_config_hash: Optional[str] = None
    fold_id: Optional[str] = None
    cost_policy_version: Optional[str] = None
    replay_id: Optional[str] = None
    input_refs: Tuple[Tuple[str, str], ...] = ()   # (name, hash) pairs, sorted on init
    authority_class: AuthorityClass = AuthorityClass.RESEARCH_WORKER
    egress_class: EgressClass = EgressClass.NONE
    work_order_hash: str = field(init=False, default="")

    def __post_init__(self) -> None:
        if not self.campaign_id or not self.task_type or not self.manifest_hash:
            raise ContractError("campaign_id, task_type, manifest_hash are required")
        if not self.dataset_snapshot_id or not self.code_commit:
            raise ContractError("dataset_snapshot_id and code_commit are required")
        if not self.seeds:
            raise ContractError("at least one deterministic seed is required")
        object.__setattr__(self, "input_refs", tuple(sorted(self.input_refs)))
        payload = dataclasses.asdict(self)
        payload.pop("work_order_hash", None)
        object.__setattr__(self, "work_order_hash", content_hash(payload))

    @property
    def attempt_id(self) -> str:
        return self.work_order_hash


class TerminalStatus(str, Enum):
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CRASHED = "crashed"


@dataclass(frozen=True)
class ResultReceipt:
    """Immutable worker output. Committed to truth only by the supervisor."""

    work_order_hash: str
    retry_seq: int
    terminal_status: TerminalStatus
    worker_id: str
    backend_id: str
    started_at: float
    ended_at: float
    environment_hash: str
    artifact_manifest: Tuple[Artifact, ...] = ()
    metrics: Tuple[Tuple[str, float], ...] = ()
    error_class: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.work_order_hash or self.retry_seq < 0:
            raise ContractError("receipt must reference an attempt")
        if self.ended_at < self.started_at:
            raise ContractError("receipt time bounds inverted")
        if self.terminal_status == TerminalStatus.COMPLETED and self.error_class:
            raise ContractError("completed receipt cannot carry an error class")
        object.__setattr__(
            self, "artifact_manifest",
            tuple(sorted(self.artifact_manifest, key=lambda a: a.ref)),
        )
        object.__setattr__(self, "metrics", tuple(sorted(self.metrics)))

    @property
    def receipt_hash(self) -> str:
        return content_hash(dataclasses.asdict(self))
