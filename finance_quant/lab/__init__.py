"""Versioned, PIT-safe parallel research laboratory."""
from .benchmark import OBSERVATION_SCHEMA, assemble_benchmark, read_temporal_observations
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
from .matrix import expand_arm_matrix
from .registry import ComponentRegistry
from .runner import BatchResult, evaluation_hash_for, router_weights, run_batch
from .shadow import ShadowPaperLab

__all__ = [
    "ArmContext", "ArmPrediction", "ArmScore", "ArmSpec", "BatchResult",
    "CanonicalOutcome", "ComponentArtifact", "ComponentRegistry", "ComponentSpec",
    "DecisionSnapshot", "ExperimentBatchSpec", "KnowledgeManifest", "LabError",
    "OBSERVATION_SCHEMA", "ShadowPaperLab", "TemporalLaneDatum", "assemble_benchmark",
    "evaluation_hash_for", "expand_arm_matrix", "freeze_snapshot", "read_temporal_observations",
    "router_weights", "run_batch",
]
