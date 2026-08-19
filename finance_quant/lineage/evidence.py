"""Cold-path lineage evidence records. Numeric time series stay in PITStore."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvidenceCommit:
    entity_type: str       # DataSnapshot | RunRecord | FeatureIR | BacktestReceipt
    entity_hash: str
    activity_type: str     # ExperimentRun | SearchTrial | AdversarialCase | PromotionReview
    known_at: str
    derived_from: tuple[str, ...] = ()
    decided_by: str | None = None

    @property
    def hash(self) -> str:
        return hashlib.blake2b(json.dumps(asdict(self), sort_keys=True).encode(), digest_size=32).hexdigest()


def evidence_payload(commit: EvidenceCommit) -> dict:
    """Payload an eventual FOSSIL dedicated-pack adapter submits for reviewed write."""
    return {"type": "finance_quant_evidence", "hash": commit.hash, **asdict(commit)}
