"""Build fixed evaluation benchmarks from immutable versioned component artifacts.

Component artifacts expose temporal observations; canonical realized outcomes stay
separate. This lets candidate agents publish new component versions without
hand-authoring snapshots or controlling the market labels used to score them.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Iterable, Mapping

from .core import CanonicalOutcome, LabError, TemporalLaneDatum, _parse_time, freeze_snapshot
from .registry import ComponentRegistry


OBSERVATION_SCHEMA = "finance-quant.lab.temporal-observations.v1"


def _outcome(row: Mapping[str, Any]) -> CanonicalOutcome:
    return CanonicalOutcome(
        str(row["entity"]),
        str(row["decision_time"]),
        str(row["outcome_time"]),
        str(row["horizon"]),
        float(row["realized_return"]),
        float(row.get("cost_bps", 0.0)),
    )


def read_temporal_observations(
    registry: ComponentRegistry,
    artifact_hash: str,
) -> tuple[TemporalLaneDatum, ...]:
    """Read and validate the standard temporal-observation payload for an artifact."""
    artifact = registry.get_required(artifact_hash)
    try:
        raw = json.loads(registry.read_payload(artifact_hash).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabError(f"component {artifact_hash} payload is not valid UTF-8 JSON") from exc
    if not isinstance(raw, Mapping) or raw.get("schema") != OBSERVATION_SCHEMA:
        raise LabError(f"component {artifact_hash} must use schema {OBSERVATION_SCHEMA!r}")
    observations = raw.get("observations")
    if not isinstance(observations, list):
        raise LabError(f"component {artifact_hash} observations must be a list")

    seen: set[tuple[str, str, str | None, str | None]] = set()
    rows: list[TemporalLaneDatum] = []
    for index, item in enumerate(observations):
        if not isinstance(item, Mapping):
            raise LabError(f"component {artifact_hash} observation[{index}] must be an object")
        entity = str(item.get("entity", ""))
        known_at = str(item.get("known_at", ""))
        if not entity or not known_at or "payload" not in item:
            raise LabError(f"component {artifact_hash} observation[{index}] requires entity, known_at, payload")
        _parse_time(known_at)
        valid_from = str(item["valid_from"]) if item.get("valid_from") is not None else None
        valid_to = str(item["valid_to"]) if item.get("valid_to") is not None else None
        if valid_from is not None:
            _parse_time(valid_from)
        if valid_to is not None:
            _parse_time(valid_to)
        key = (entity, known_at, valid_from, valid_to)
        if key in seen:
            raise LabError(
                f"component {artifact_hash} has duplicate temporal observation identity {key}; "
                "aggregate it inside the component"
            )
        seen.add(key)
        datum = TemporalLaneDatum.from_payload(
            artifact.lane,
            artifact_hash,
            known_at,
            {"entity": entity, "value": item["payload"]},
            valid_from=valid_from,
            valid_to=valid_to,
        )
        rows.append(datum)
    return tuple(rows)


def _entity_payload(datum: TemporalLaneDatum) -> tuple[str, Any]:
    raw = json.loads(datum.payload_json)
    return str(raw["entity"]), raw["value"]


def assemble_benchmark(
    evaluation: Mapping[str, Any],
    registry: ComponentRegistry,
    artifact_hashes: Iterable[str],
) -> dict[str, Any]:
    """Freeze all requested component versions at each canonical decision cut."""
    experiment = evaluation.get("experiment")
    if not isinstance(experiment, Mapping):
        raise LabError("evaluation must contain an experiment object")
    raw_outcomes = evaluation.get("outcomes")
    if not isinstance(raw_outcomes, list) or not raw_outcomes:
        raise LabError("evaluation must contain at least one canonical outcome")
    outcomes = tuple(_outcome(row) for row in raw_outcomes)
    horizon = str(experiment.get("outcome_horizon", ""))
    if not horizon or any(outcome.horizon != horizon for outcome in outcomes):
        raise LabError("all canonical outcomes must match experiment outcome_horizon")
    keys = [outcome.key for outcome in outcomes]
    if len(keys) != len(set(keys)):
        raise LabError("evaluation contains duplicate canonical outcome keys")

    hashes = tuple(sorted(set(str(value) for value in artifact_hashes)))
    if not hashes:
        raise LabError("benchmark assembly requires at least one component artifact")

    artifact_rows: dict[str, tuple[TemporalLaneDatum, ...]] = {}
    component_meta: list[dict[str, str]] = []
    for artifact_hash in hashes:
        artifact = registry.get_required(artifact_hash)
        artifact_rows[artifact_hash] = read_temporal_observations(registry, artifact_hash)
        component_meta.append(
            {
                "artifact_hash": artifact_hash,
                "lane": artifact.lane,
                "component_name": artifact.component_name,
                "component_version": artifact.component_version,
                "spec_hash": artifact.spec_hash,
                "payload_hash": artifact.payload_hash,
            }
        )

    snapshots: list[dict[str, Any]] = []
    for outcome in sorted(outcomes, key=lambda item: (item.decision_time, item.entity, item.horizon)):
        candidates: list[TemporalLaneDatum] = []
        for artifact_hash in hashes:
            for datum in artifact_rows[artifact_hash]:
                entity, value = _entity_payload(datum)
                if entity not in {outcome.entity, "*"}:
                    continue
                candidates.append(
                    TemporalLaneDatum.from_payload(
                        datum.lane,
                        datum.artifact_hash,
                        datum.known_at,
                        value,
                        valid_from=datum.valid_from,
                        valid_to=datum.valid_to,
                    )
                )
        snapshot = freeze_snapshot(outcome.entity, outcome.decision_time, outcome.horizon, candidates)
        snapshots.append(
            {
                "entity": snapshot.entity,
                "decision_time": snapshot.decision_time,
                "horizon": snapshot.horizon,
                "snapshot_id": snapshot.snapshot_id,
                "data": [
                    {
                        "lane": item.lane,
                        "artifact_hash": item.artifact_hash,
                        "known_at": item.known_at,
                        "payload": item.payload,
                    }
                    for item in snapshot.lanes
                ],
            }
        )

    return {
        "experiment": dict(experiment),
        "components": sorted(component_meta, key=lambda row: (row["lane"], row["component_version"], row["artifact_hash"])),
        "snapshots": snapshots,
        "outcomes": [asdict(outcome) for outcome in outcomes],
    }
