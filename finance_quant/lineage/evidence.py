"""Cold-path lineage evidence records. Numeric time series stay in PITStore."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


ENTITY_TYPES = {"DataSnapshot", "RunRecord", "FeatureIR", "ModelArtifact",
                "BacktestReceipt"}
ACTIVITY_TYPES = {"ExperimentRun", "SearchTrial", "AdversarialCase", "PromotionReview",
                  "DataIngest"}


class OntologyError(ValueError):
    """Raised when an evidence commit violates the v0.1 ontology boundary."""


@dataclass(frozen=True)
class EvidenceCommit:
    entity_type: str       # DataSnapshot | RunRecord | FeatureIR | BacktestReceipt
    entity_hash: str
    activity_type: str     # ExperimentRun | SearchTrial | AdversarialCase | PromotionReview
    known_at: str
    derived_from: tuple[str, ...] = ()
    decided_by: str | None = None

    def __post_init__(self) -> None:
        if self.entity_type not in ENTITY_TYPES:
            raise OntologyError(f"unknown entity_type: {self.entity_type}")
        if self.activity_type not in ACTIVITY_TYPES:
            raise OntologyError(f"unknown activity_type: {self.activity_type}")
        if self.activity_type == "PromotionReview" and not self.decided_by:
            raise OntologyError("PromotionReview requires decided_by")
        if not self.entity_hash:
            raise OntologyError("entity_hash is required")
        if not self.known_at:
            raise OntologyError("known_at is required")

    @property
    def hash(self) -> str:
        return hashlib.blake2b(json.dumps(asdict(self), sort_keys=True).encode(), digest_size=32).hexdigest()


def evidence_payload(commit: EvidenceCommit) -> dict:
    """Payload an eventual FOSSIL dedicated-pack adapter submits for reviewed write."""
    return {"type": "finance_quant_evidence", "hash": commit.hash, **asdict(commit)}
