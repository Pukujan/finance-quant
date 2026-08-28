from __future__ import annotations

import json

from finance_quant.lab.core import ArmSpec, CanonicalOutcome, ExperimentBatchSpec, TemporalLaneDatum, freeze_snapshot
from finance_quant.lab.runner import run_batch, run_spec_for


T0 = "2024-01-02T16:00:00+00:00"
T1 = "2024-01-03T16:00:00+00:00"


def _arm() -> ArmSpec:
    return ArmSpec(
        "price",
        (("price", "price-v1"),),
        "finance_quant.lab.demo:weighted_signal",
        model_config_json=json.dumps({"weights": {"price": 1.0}}),
    )


def _batch(arm: ArmSpec) -> ExperimentBatchSpec:
    return ExperimentBatchSpec(
        "evaluation-identity",
        "code",
        "env",
        "human-label-can-stay-the-same",
        "wfo",
        "2bps",
        (1,),
        "1d",
        (arm,),
    )


def test_actual_outcome_and_snapshot_content_are_part_of_run_identity():
    arm = _arm()
    batch = _batch(arm)
    snapshot = freeze_snapshot(
        "AAA",
        T0,
        "1d",
        (TemporalLaneDatum.from_payload("price", "price-v1", T0, {"signal": 0.01}),),
    )
    changed_snapshot = freeze_snapshot(
        "AAA",
        T0,
        "1d",
        (TemporalLaneDatum.from_payload("price", "price-v1", T0, {"signal": 0.011}),),
    )
    outcome_a = CanonicalOutcome("AAA", T0, T1, "1d", 0.01, 2.0)
    outcome_b = CanonicalOutcome("AAA", T0, T1, "1d", -0.02, 2.0)

    result_a = run_batch(batch, (snapshot,), (outcome_a,))
    result_changed_outcome = run_batch(batch, (snapshot,), (outcome_b,))
    result_changed_snapshot = run_batch(batch, (changed_snapshot,), (outcome_a,))

    assert result_a.evaluation_hash != result_changed_outcome.evaluation_hash
    assert result_a.evaluation_hash != result_changed_snapshot.evaluation_hash

    run_a = run_spec_for(batch, arm, result_a.evaluation_hash)
    run_b = run_spec_for(batch, arm, result_changed_outcome.evaluation_hash)
    assert run_a.idempotency_key != run_b.idempotency_key
