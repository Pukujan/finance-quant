"""Deterministic campaign expansion: campaign spec -> hashable manifest of WorkOrders.

The manifest is hashable and auditable so the expected attempt set — and hence
fan-in completeness — is known before any execution starts (issue #10).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Optional, Tuple

from .contracts import (AuthorityClass, EgressClass, ResourceRequest, WorkOrder,
                        content_hash)

_EXPANSION_DIMS = ("factor_hash", "model_config_hash", "fold_id",
                   "cost_policy_version", "replay_id")


@dataclass(frozen=True)
class StageSpec:
    """One stage of the grid, e.g. train+predict; replay stages may depend via input_refs."""
    task_type: str
    dimensions: Tuple[Tuple[str, Tuple[str, ...]], ...]  # ordered (name, values)
    authority_class: AuthorityClass = AuthorityClass.RESEARCH_WORKER
    egress_class: EgressClass = EgressClass.NONE

    def __post_init__(self) -> None:
        # Canonicalize: dimension order in the spec must not change identity.
        dims = tuple(sorted(self.dimensions, key=lambda d: d[0]))
        object.__setattr__(self, "dimensions", dims)
        names = [n for n, _ in dims]
        if any(n not in _EXPANSION_DIMS for n in names):
            raise ValueError(f"unknown expansion dimension in {names}")


@dataclass(frozen=True)
class CampaignSpec:
    campaign_id: str
    dataset_snapshot_id: str
    code_commit: str
    seeds: Tuple[int, ...]
    stages: Tuple[StageSpec, ...]
    resource_request: ResourceRequest = ResourceRequest()


@dataclass(frozen=True)
class ExpansionManifest:
    campaign_id: str
    work_orders: Tuple[WorkOrder, ...]
    manifest_hash: str

    @property
    def expected_attempt_ids(self) -> Tuple[str, ...]:
        return tuple(wo.attempt_id for wo in self.work_orders)


def expand_campaign(spec: CampaignSpec,
                    manifest_nonce: str = "v0") -> ExpansionManifest:
    """Deterministic product expansion, canonical ordering by dimension tuple."""
    manifest_seed = content_hash({
        "nonce": manifest_nonce,
        "spec": spec,
    })

    orders: list[WorkOrder] = []
    for stage_index, stage in enumerate(spec.stages):
        dim_names = [n for n, _ in stage.dimensions]
        dim_values = [sorted(v) for _, v in stage.dimensions]
        for combo in itertools.product(*dim_values):
            dims = dict(zip(dim_names, combo))
            orders.append(WorkOrder(
                campaign_id=spec.campaign_id,
                task_type=stage.task_type,
                dataset_snapshot_id=spec.dataset_snapshot_id,
                code_commit=spec.code_commit,
                seeds=spec.seeds,
                manifest_hash=manifest_seed,
                resource_request=spec.resource_request,
                factor_hash=dims.get("factor_hash"),
                model_config_hash=dims.get("model_config_hash"),
                fold_id=dims.get("fold_id"),
                cost_policy_version=dims.get("cost_policy_version"),
                replay_id=dims.get("replay_id"),
                authority_class=stage.authority_class,
                egress_class=stage.egress_class,
            ))
    # Canonical order: lexicographic by the full dimension tuple, then task.
    orders.sort(key=lambda w: (w.factor_hash or "", w.model_config_hash or "",
                               w.fold_id or "", w.cost_policy_version or "",
                               w.replay_id or "", w.task_type))
    manifest_hash = content_hash({
        "seed": manifest_seed,
        "attempt_ids": [w.attempt_id for w in orders],
    })
    return ExpansionManifest(
        campaign_id=spec.campaign_id,
        work_orders=tuple(orders),
        manifest_hash=manifest_hash,
    )
