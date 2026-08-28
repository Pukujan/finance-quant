"""Declarative arm matrix expansion for cheap parallel experimentation."""
from __future__ import annotations

import itertools
from typing import Any, Mapping

from .core import ArmSpec, LabError, canonical_json


def _component(item: Any, *, context: str) -> tuple[str, str]:
    if not isinstance(item, Mapping):
        raise LabError(f"{context} component must be an object")
    lane = str(item.get("lane", ""))
    artifact_hash = str(item.get("artifact_hash", ""))
    if not lane or not artifact_hash:
        raise LabError(f"{context} component requires lane and artifact_hash")
    return lane, artifact_hash


def expand_arm_matrix(raw: Mapping[str, Any]) -> tuple[ArmSpec, ...]:
    """Expand explicitly requested component/model combinations into exact arms.

    The matrix never invents which lane combinations should be tested. Callers
    provide `combinations`, which keeps combinatorial growth visible and bounded.
    """
    base_rows = raw.get("base_components", [])
    if not isinstance(base_rows, list):
        raise LabError("matrix base_components must be a list")
    base = tuple(_component(item, context="base") for item in base_rows)
    base_lanes = [lane for lane, _ in base]
    if len(base_lanes) != len(set(base_lanes)):
        raise LabError("matrix base_components cannot repeat a lane")

    raw_variants = raw.get("variant_lanes")
    if not isinstance(raw_variants, Mapping) or not raw_variants:
        raise LabError("matrix variant_lanes must be a non-empty object")
    variants: dict[str, tuple[tuple[str, str], ...]] = {}
    for lane_raw, rows in raw_variants.items():
        lane = str(lane_raw)
        if lane in base_lanes:
            raise LabError(f"variant lane {lane!r} is already fixed in base_components")
        if not isinstance(rows, list) or not rows:
            raise LabError(f"variant lane {lane!r} must have at least one version")
        parsed: list[tuple[str, str]] = []
        seen_names: set[str] = set()
        seen_artifacts: set[str] = set()
        for item in rows:
            if not isinstance(item, Mapping):
                raise LabError(f"variant lane {lane!r} entries must be objects")
            name = str(item.get("name", ""))
            artifact_hash = str(item.get("artifact_hash", ""))
            if not name or not artifact_hash:
                raise LabError(f"variant lane {lane!r} entries require name and artifact_hash")
            if name in seen_names or artifact_hash in seen_artifacts:
                raise LabError(f"variant lane {lane!r} contains duplicate names or artifacts")
            seen_names.add(name)
            seen_artifacts.add(artifact_hash)
            parsed.append((name, artifact_hash))
        variants[lane] = tuple(parsed)

    raw_combinations = raw.get("combinations")
    if not isinstance(raw_combinations, list) or not raw_combinations:
        raise LabError("matrix combinations must be a non-empty list; include [] explicitly for a baseline")
    combinations: list[tuple[str, ...]] = []
    seen_combinations: set[tuple[str, ...]] = set()
    for combo in raw_combinations:
        if not isinstance(combo, list):
            raise LabError("each matrix combination must be a list of variant lane names")
        normalized = tuple(sorted(str(lane) for lane in combo))
        if len(normalized) != len(set(normalized)):
            raise LabError("a matrix combination cannot repeat a lane")
        unknown = [lane for lane in normalized if lane not in variants]
        if unknown:
            raise LabError(f"matrix combination references unknown variant lanes: {unknown}")
        if normalized in seen_combinations:
            raise LabError(f"duplicate matrix combination: {normalized}")
        seen_combinations.add(normalized)
        combinations.append(normalized)

    raw_models = raw.get("models")
    if not isinstance(raw_models, list) or not raw_models:
        raise LabError("matrix models must be a non-empty list")
    models: list[Mapping[str, Any]] = []
    model_names: set[str] = set()
    for model in raw_models:
        if not isinstance(model, Mapping):
            raise LabError("matrix model entries must be objects")
        name = str(model.get("name", ""))
        executor_ref = str(model.get("executor_ref", ""))
        if not name or not executor_ref:
            raise LabError("matrix model entries require name and executor_ref")
        if name in model_names:
            raise LabError(f"duplicate matrix model name: {name}")
        model_names.add(name)
        models.append(model)

    max_arms = int(raw.get("max_arms", 1000))
    if max_arms < 1:
        raise LabError("matrix max_arms must be positive")

    projected = 0
    for combo in combinations:
        multiplier = 1
        for lane in combo:
            multiplier *= len(variants[lane])
        projected += multiplier * len(models)
    if projected > max_arms:
        raise LabError(f"matrix would create {projected} arms, above max_arms={max_arms}")

    prefix = str(raw.get("id_prefix", ""))
    arms: list[ArmSpec] = []
    for model in models:
        model_name = str(model["name"])
        for combo in combinations:
            choices = [variants[lane] for lane in combo]
            products = itertools.product(*choices) if choices else [()]
            for selected in products:
                selected_components = tuple((lane, artifact_hash) for lane, (_, artifact_hash) in zip(combo, selected))
                components = base + selected_components
                suffix = "base" if not combo else "+".join(
                    f"{lane}={variant_name}" for lane, (variant_name, _) in zip(combo, selected)
                )
                arm_id = f"{prefix}{model_name}::{suffix}"
                arms.append(
                    ArmSpec(
                        arm_id=arm_id,
                        components=components,
                        executor_ref=str(model["executor_ref"]),
                        model_config_json=canonical_json(model.get("model_config", {})),
                        retrieval_policy_json=canonical_json(model.get("retrieval_policy", {})),
                        feature_projection_json=canonical_json(model.get("feature_projection", {})),
                        portfolio_policy_json=canonical_json(model.get("portfolio_policy", {})),
                    )
                )
    return tuple(arms)
