"""Fixed semantics for the parallel research laboratory.

Candidate components/models may vary. Historical cuts, arm identity, realized
outcomes, and scoring semantics live here so candidates cannot silently change
their benchmark.
"""
from __future__ import annotations

import hashlib
import importlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Iterable


class LabError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def content_hash(value: Any) -> str:
    return hashlib.blake2b(canonical_json(value).encode("utf-8"), digest_size=32).hexdigest()


def _parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise LabError(f"invalid ISO timestamp: {value}") from exc


@dataclass(frozen=True)
class ComponentSpec:
    lane: str
    name: str
    version: str
    code_sha: str
    input_dataset_manifest_hash: str
    schema_version: str = "1"
    ontology_version: str = "1"
    model_or_extractor_hash: str = ""
    parameters_json: str = "{}"
    knowledge_cut_or_build_range: str = ""
    parent_artifact_hashes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = (self.lane, self.name, self.version, self.code_sha, self.input_dataset_manifest_hash)
        if not all(required):
            raise LabError("component identity fields cannot be empty")
        try:
            parsed = json.loads(self.parameters_json)
        except json.JSONDecodeError as exc:
            raise LabError("parameters_json must be valid JSON") from exc
        object.__setattr__(self, "parameters_json", canonical_json(parsed))
        object.__setattr__(self, "parent_artifact_hashes", tuple(sorted(set(self.parent_artifact_hashes))))

    @property
    def spec_hash(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class ComponentArtifact:
    artifact_hash: str
    spec_hash: str
    lane: str
    component_name: str
    component_version: str
    payload_hash: str
    parent_artifact_hashes: tuple[str, ...]
    metadata_path: str
    payload_path: str


@dataclass(frozen=True)
class KnowledgeManifest:
    """Exact component artifact selected for each semantic knowledge lane."""

    components: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        normalized = tuple(sorted((str(lane), str(artifact)) for lane, artifact in self.components))
        lanes = [lane for lane, _ in normalized]
        if len(lanes) != len(set(lanes)):
            raise LabError("knowledge manifest can reference at most one artifact per lane")
        if any(not lane or not artifact for lane, artifact in normalized):
            raise LabError("manifest entries cannot be empty")
        object.__setattr__(self, "components", normalized)

    @property
    def manifest_hash(self) -> str:
        return content_hash(self.components)

    def artifact_for(self, lane: str) -> str:
        for candidate, artifact in self.components:
            if candidate == lane:
                return artifact
        raise KeyError(lane)


@dataclass(frozen=True)
class TemporalLaneDatum:
    """One versioned component value before the decision-time freeze."""

    lane: str
    artifact_hash: str
    known_at: str
    payload_json: str
    valid_from: str | None = None
    valid_to: str | None = None

    @classmethod
    def from_payload(
        cls,
        lane: str,
        artifact_hash: str,
        known_at: str,
        payload: Any,
        *,
        valid_from: str | None = None,
        valid_to: str | None = None,
    ) -> "TemporalLaneDatum":
        if not lane or not artifact_hash:
            raise LabError("lane and artifact_hash are required")
        return cls(lane, artifact_hash, known_at, canonical_json(payload), valid_from, valid_to)

    @property
    def component_key(self) -> tuple[str, str]:
        return self.lane, self.artifact_hash

    def is_visible(self, decision_time: str) -> bool:
        decision = _parse_time(decision_time)
        if _parse_time(self.known_at) > decision:
            return False
        if self.valid_from is not None and _parse_time(self.valid_from) > decision:
            return False
        if self.valid_to is not None and _parse_time(self.valid_to) < decision:
            return False
        return True


@dataclass(frozen=True)
class LaneValue:
    lane: str
    artifact_hash: str
    known_at: str
    payload_json: str

    @property
    def component_key(self) -> tuple[str, str]:
        return self.lane, self.artifact_hash

    @property
    def payload(self) -> Any:
        return json.loads(self.payload_json)


@dataclass(frozen=True)
class DecisionSnapshot:
    """All visible component versions at one historical decision cut.

    Multiple artifacts for the same semantic lane are intentionally allowed so
    arms can compare `news@v3` and `news@v4` against the same market outcome.
    """

    entity: str
    decision_time: str
    horizon: str
    lanes: tuple[LaneValue, ...]

    def __post_init__(self) -> None:
        decision = _parse_time(self.decision_time)
        if not self.entity or not self.horizon:
            raise LabError("snapshot entity/horizon cannot be empty")
        normalized = tuple(sorted(self.lanes, key=lambda item: (item.lane, item.artifact_hash)))
        keys = [item.component_key for item in normalized]
        if len(keys) != len(set(keys)):
            raise LabError("snapshot must contain at most one frozen value per component artifact")
        for item in normalized:
            if _parse_time(item.known_at) > decision:
                raise LabError(f"future-known component {item.component_key!r} leaked into snapshot")
        object.__setattr__(self, "lanes", normalized)

    @property
    def snapshot_id(self) -> str:
        return content_hash(asdict(self))


def freeze_snapshot(
    entity: str,
    decision_time: str,
    horizon: str,
    data: Iterable[TemporalLaneDatum],
) -> DecisionSnapshot:
    """Filter before arm selection/ranking; preserve side-by-side component versions.

    If one immutable component artifact emits multiple temporally versioned rows,
    the latest row visible at the decision cut is kept for that exact artifact.
    Different artifacts in the same lane remain independently addressable.
    """
    visible: dict[tuple[str, str], TemporalLaneDatum] = {}
    for item in data:
        if not item.is_visible(decision_time):
            continue
        key = item.component_key
        prior = visible.get(key)
        if prior is None or _parse_time(item.known_at) > _parse_time(prior.known_at):
            visible[key] = item
    lanes = tuple(
        LaneValue(item.lane, item.artifact_hash, item.known_at, item.payload_json)
        for item in visible.values()
    )
    return DecisionSnapshot(entity, decision_time, horizon, lanes)


@dataclass(frozen=True)
class ArmSpec:
    """Complete candidate hypothesis with exact component versions declared.

    `components` contains one `(lane, artifact_hash)` pair per consumed lane. The
    manifest hash is derived, never supplied by candidate code.
    """

    arm_id: str
    components: tuple[tuple[str, str], ...]
    executor_ref: str
    model_config_json: str = "{}"
    retrieval_policy_json: str = "{}"
    feature_projection_json: str = "{}"
    portfolio_policy_json: str = "{}"

    def __post_init__(self) -> None:
        if not self.arm_id or not self.executor_ref:
            raise LabError("arm_id and executor_ref are required")
        manifest = KnowledgeManifest(self.components)
        if not manifest.components:
            raise LabError("arm must declare at least one component")
        object.__setattr__(self, "components", manifest.components)
        for field in (
            "model_config_json",
            "retrieval_policy_json",
            "feature_projection_json",
            "portfolio_policy_json",
        ):
            raw = getattr(self, field)
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise LabError(f"{field} must be valid JSON") from exc
            object.__setattr__(self, field, canonical_json(parsed))

    @property
    def knowledge_manifest(self) -> KnowledgeManifest:
        return KnowledgeManifest(self.components)

    @property
    def knowledge_manifest_hash(self) -> str:
        return self.knowledge_manifest.manifest_hash

    @property
    def lanes(self) -> tuple[str, ...]:
        return tuple(lane for lane, _ in self.components)

    @property
    def model_config_hash(self) -> str:
        return content_hash(json.loads(self.model_config_json))

    @property
    def retrieval_policy_hash(self) -> str:
        return content_hash(json.loads(self.retrieval_policy_json))

    @property
    def feature_projection_hash(self) -> str:
        return content_hash(json.loads(self.feature_projection_json))

    @property
    def portfolio_policy_hash(self) -> str:
        return content_hash(json.loads(self.portfolio_policy_json))

    @property
    def arm_spec_hash(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class ExperimentBatchSpec:
    experiment_id: str
    code_sha: str
    env_lock_hash: str
    dataset_manifest_hash: str
    split_policy_ref: str
    cost_model_ref: str
    seeds: tuple[int, ...]
    outcome_horizon: str
    arms: tuple[ArmSpec, ...]

    def __post_init__(self) -> None:
        required = (
            self.experiment_id,
            self.code_sha,
            self.env_lock_hash,
            self.dataset_manifest_hash,
            self.split_policy_ref,
            self.cost_model_ref,
            self.outcome_horizon,
        )
        if not all(required) or not self.seeds or not self.arms:
            raise LabError("batch reproducibility fields, seeds, and arms are required")
        arm_ids = [arm.arm_id for arm in self.arms]
        if len(arm_ids) != len(set(arm_ids)):
            raise LabError("arm ids must be unique in a batch")

    @property
    def batch_hash(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class ArmContext:
    entity: str
    decision_time: str
    horizon: str
    snapshot_id: str
    lanes: tuple[LaneValue, ...]
    config_json: str

    def lane_payload(self, lane: str) -> Any:
        for item in self.lanes:
            if item.lane == lane:
                return item.payload
        raise KeyError(lane)

    def artifact_for(self, lane: str) -> str:
        for item in self.lanes:
            if item.lane == lane:
                return item.artifact_hash
        raise KeyError(lane)

    @property
    def config(self) -> Any:
        return json.loads(self.config_json)


def arm_context(snapshot: DecisionSnapshot, arm: ArmSpec) -> ArmContext:
    by_component = {item.component_key: item for item in snapshot.lanes}
    missing = [component for component in arm.components if component not in by_component]
    if missing:
        raise LabError(f"snapshot missing arm components: {missing}")
    selected = tuple(by_component[component] for component in arm.components)
    return ArmContext(
        snapshot.entity,
        snapshot.decision_time,
        snapshot.horizon,
        snapshot.snapshot_id,
        selected,
        arm.model_config_json,
    )


@dataclass(frozen=True)
class CanonicalOutcome:
    entity: str
    decision_time: str
    outcome_time: str
    horizon: str
    realized_return: float
    cost_bps: float = 0.0

    def __post_init__(self) -> None:
        if _parse_time(self.outcome_time) <= _parse_time(self.decision_time):
            raise LabError("outcome must resolve strictly after decision time")
        if self.cost_bps < 0:
            raise LabError("cost_bps cannot be negative")

    @property
    def key(self) -> tuple[str, str, str]:
        return self.entity, self.decision_time, self.horizon

    @property
    def outcome_id(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class ArmPrediction:
    arm_id: str
    entity: str
    decision_time: str
    horizon: str
    snapshot_id: str
    predicted_return: float

    @property
    def key(self) -> tuple[str, str, str]:
        return self.entity, self.decision_time, self.horizon


@dataclass(frozen=True)
class ArmScore:
    arm_id: str
    entity: str
    decision_time: str
    outcome_time: str
    horizon: str
    outcome_id: str
    predicted_return: float
    realized_return: float
    error: float
    absolute_error: float
    squared_error: float
    direction_hit: float
    strategy_net_return: float


def score_prediction(prediction: ArmPrediction, outcome: CanonicalOutcome) -> ArmScore:
    if prediction.key != outcome.key:
        raise LabError("prediction/outcome key mismatch")
    error = prediction.predicted_return - outcome.realized_return
    direction_hit = float((prediction.predicted_return >= 0) == (outcome.realized_return >= 0))
    strategy = 0.0
    if prediction.predicted_return > 0:
        strategy = outcome.realized_return - outcome.cost_bps / 10_000.0
    return ArmScore(
        prediction.arm_id,
        prediction.entity,
        prediction.decision_time,
        outcome.outcome_time,
        prediction.horizon,
        outcome.outcome_id,
        prediction.predicted_return,
        outcome.realized_return,
        error,
        abs(error),
        error * error,
        direction_hit,
        strategy,
    )


Executor = Callable[[ArmContext], float]


def load_executor(ref: str) -> Executor:
    if ":" not in ref:
        raise LabError("executor_ref must be 'module:function'")
    module_name, attr = ref.split(":", 1)
    module = importlib.import_module(module_name)
    executor = getattr(module, attr, None)
    if not callable(executor):
        raise LabError(f"executor {ref!r} is not callable")
    return executor
