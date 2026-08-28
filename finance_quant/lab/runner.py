"""Parallel full-information arm executor.

Executors receive only frozen decision-time contexts. Realized outcomes remain in
this module and are joined after every candidate has predicted.
"""
from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus

from .core import (
    ArmPrediction,
    ArmScore,
    ArmSpec,
    CanonicalOutcome,
    DecisionSnapshot,
    ExperimentBatchSpec,
    KnowledgeManifest,
    LabError,
    _parse_time,
    arm_context,
    load_executor,
    score_prediction,
)


@dataclass(frozen=True)
class ArmSummary:
    arm_id: str
    count: int
    directional_accuracy: float
    mae: float
    rmse: float
    mean_strategy_net_return: float
    compounded_strategy_net_return: float


@dataclass(frozen=True)
class BatchResult:
    batch_hash: str
    predictions: tuple[ArmPrediction, ...]
    scores: tuple[ArmScore, ...]
    summaries: tuple[ArmSummary, ...]

    def to_dict(self) -> dict:
        return {
            "batch_hash": self.batch_hash,
            "predictions": [asdict(item) for item in self.predictions],
            "scores": [asdict(item) for item in self.scores],
            "summaries": [asdict(item) for item in self.summaries],
        }


def _summary(arm_id: str, scores: Sequence[ArmScore]) -> ArmSummary:
    rows = [score for score in scores if score.arm_id == arm_id]
    if not rows:
        return ArmSummary(arm_id, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    count = len(rows)
    mae = sum(row.absolute_error for row in rows) / count
    rmse = math.sqrt(sum(row.squared_error for row in rows) / count)
    hit = sum(row.direction_hit for row in rows) / count
    mean_net = sum(row.strategy_net_return for row in rows) / count
    capital = 1.0
    for row in sorted(rows, key=lambda x: (x.decision_time, x.entity)):
        capital *= 1.0 + row.strategy_net_return
    return ArmSummary(arm_id, count, hit, mae, rmse, mean_net, capital - 1.0)


def run_spec_for(batch: ExperimentBatchSpec, arm: ArmSpec) -> RunSpec:
    return RunSpec(
        experiment_id=f"{batch.experiment_id}:{arm.arm_id}",
        code_sha=batch.code_sha,
        env_lock_hash=batch.env_lock_hash,
        dataset_manifest_hash=batch.dataset_manifest_hash,
        feature_ir_hash=arm.feature_projection_hash,
        model_config_hash=arm.model_config_hash,
        seeds=batch.seeds,
        split_policy_ref=batch.split_policy_ref,
        cost_model_ref=batch.cost_model_ref,
        agent_origin="lab",
        knowledge_manifest_hash=arm.knowledge_manifest_hash,
        retrieval_policy_hash=arm.retrieval_policy_hash,
        arm_spec_hash=arm.arm_spec_hash,
        router_config_hash="",
    )


def _validate_arm_manifest(snapshot: DecisionSnapshot, arm: ArmSpec) -> None:
    context = arm_context(snapshot, arm)
    actual = KnowledgeManifest(tuple((item.lane, item.artifact_hash) for item in context.lanes))
    if actual.manifest_hash != arm.knowledge_manifest_hash:
        raise LabError(
            f"arm {arm.arm_id!r} manifest does not match its exact frozen component artifacts "
            f"at {snapshot.entity}/{snapshot.decision_time}"
        )


def _predict(snapshot: DecisionSnapshot, arm: ArmSpec) -> ArmPrediction:
    _validate_arm_manifest(snapshot, arm)
    context = arm_context(snapshot, arm)
    executor = load_executor(arm.executor_ref)
    value = float(executor(context))
    if not math.isfinite(value):
        raise LabError(f"arm {arm.arm_id} produced non-finite prediction")
    return ArmPrediction(
        arm.arm_id,
        snapshot.entity,
        snapshot.decision_time,
        snapshot.horizon,
        snapshot.snapshot_id,
        value,
    )


def run_batch(
    batch: ExperimentBatchSpec,
    snapshots: Sequence[DecisionSnapshot],
    outcomes: Sequence[CanonicalOutcome],
    *,
    max_workers: int = 1,
    ledger: ExperimentLedger | None = None,
) -> BatchResult:
    if max_workers < 1:
        raise LabError("max_workers must be >= 1")
    if any(snapshot.horizon != batch.outcome_horizon for snapshot in snapshots):
        raise LabError("snapshot horizon disagrees with batch")
    if any(outcome.horizon != batch.outcome_horizon for outcome in outcomes):
        raise LabError("outcome horizon disagrees with batch")

    outcome_by_key: dict[tuple[str, str, str], CanonicalOutcome] = {}
    for outcome in outcomes:
        if outcome.key in outcome_by_key and outcome_by_key[outcome.key] != outcome:
            raise LabError(f"multiple canonical outcomes for {outcome.key}")
        outcome_by_key[outcome.key] = outcome

    expected_keys = {(snapshot.entity, snapshot.decision_time, snapshot.horizon) for snapshot in snapshots}
    if expected_keys != set(outcome_by_key):
        missing = expected_keys - set(outcome_by_key)
        extra = set(outcome_by_key) - expected_keys
        raise LabError(f"canonical outcome coverage mismatch missing={sorted(missing)} extra={sorted(extra)}")

    for snapshot in snapshots:
        for arm in batch.arms:
            _validate_arm_manifest(snapshot, arm)

    tasks = [(snapshot, arm) for snapshot in snapshots for arm in batch.arms]
    if max_workers == 1:
        predictions = [_predict(snapshot, arm) for snapshot, arm in tasks]
    else:
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="finance-quant-arm") as pool:
            futures = [pool.submit(_predict, snapshot, arm) for snapshot, arm in tasks]
            predictions = [future.result() for future in futures]

    predictions.sort(key=lambda item: (item.decision_time, item.entity, item.arm_id))
    scores = [score_prediction(prediction, outcome_by_key[prediction.key]) for prediction in predictions]
    scores.sort(key=lambda item: (item.decision_time, item.entity, item.arm_id))

    arm_ids = {arm.arm_id for arm in batch.arms}
    for key in expected_keys:
        key_scores = [score for score in scores if (score.entity, score.decision_time, score.horizon) == key]
        if {score.arm_id for score in key_scores} != arm_ids:
            raise LabError(f"not every arm was scored at {key}")
        if len({score.outcome_id for score in key_scores}) != 1:
            raise LabError(f"arms received different outcomes at {key}")

    summaries = tuple(_summary(arm.arm_id, scores) for arm in sorted(batch.arms, key=lambda x: x.arm_id))

    if ledger is not None:
        by_arm = {summary.arm_id: summary for summary in summaries}
        for arm in batch.arms:
            record = ledger.begin(run_spec_for(batch, arm))
            summary = by_arm[arm.arm_id]
            metrics = {
                "count": float(summary.count),
                "directional_accuracy": summary.directional_accuracy,
                "mae": summary.mae,
                "rmse": summary.rmse,
                "mean_strategy_net_return": summary.mean_strategy_net_return,
                "compounded_strategy_net_return": summary.compounded_strategy_net_return,
            }
            ledger.finalize(
                record.run_id,
                RunStatus.SUCCESS,
                metrics=metrics,
                artifacts={"batch_hash": batch.batch_hash, "arm_spec_hash": arm.arm_spec_hash},
            )

    return BatchResult(batch.batch_hash, tuple(predictions), tuple(scores), summaries)


def router_weights(
    arm_ids: Sequence[str],
    decision_time: str,
    score_history: Iterable[ArmScore],
    *,
    eta: float = 8.0,
) -> dict[str, float]:
    """Inspectable exponentially-weighted experts using resolved OOS returns only."""
    ids = tuple(sorted(set(arm_ids)))
    if not ids:
        raise LabError("router needs at least one arm")
    if eta < 0:
        raise LabError("eta cannot be negative")

    rewards = {arm_id: 0.0 for arm_id in ids}
    for score in score_history:
        if score.arm_id not in rewards:
            continue
        if _parse_time(score.outcome_time) <= _parse_time(decision_time):
            rewards[score.arm_id] += score.strategy_net_return

    raw = {arm_id: math.exp(max(-60.0, min(60.0, eta * reward))) for arm_id, reward in rewards.items()}
    total = sum(raw.values())
    return {arm_id: raw[arm_id] / total for arm_id in ids}
