"""Versioned, PIT-safe parallel research laboratory."""
from .core import (
    ArmContext,
    ArmPrediction,
    ArmScore,
    ArmSpec,
    CanonicalOutcome,
    ComponentArtifact,
    ComponentSpec,
    DecisionSnapshot,
    ExperimentBatchSpec,
    KnowledgeManifest,
    LabError,
    TemporalLaneDatum,
    freeze_snapshot,
)
from .registry import ComponentRegistry
from .runner import BatchResult, router_weights, run_batch

__all__ = [
    "ArmContext", "ArmPrediction", "ArmScore", "ArmSpec", "BatchResult",
    "CanonicalOutcome", "ComponentArtifact", "ComponentRegistry", "ComponentSpec",
    "DecisionSnapshot", "ExperimentBatchSpec", "KnowledgeManifest", "LabError",
    "TemporalLaneDatum", "freeze_snapshot", "router_weights", "run_batch",
]
