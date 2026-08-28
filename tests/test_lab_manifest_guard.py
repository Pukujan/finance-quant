import json

import pytest

from finance_quant.lab.core import ArmSpec, CanonicalOutcome, ExperimentBatchSpec, LabError, TemporalLaneDatum, freeze_snapshot
from finance_quant.lab.runner import run_batch


def test_arm_cannot_select_an_artifact_not_present_in_frozen_snapshot():
    t0 = "2024-01-02T16:00:00+00:00"
    t1 = "2024-01-03T16:00:00+00:00"
    snapshot = freeze_snapshot(
        "AAA",
        t0,
        "1d",
        (TemporalLaneDatum.from_payload("price", "price-v1", t0, {"signal": 0.01}),),
    )
    arm = ArmSpec(
        "bad-component",
        (("price", "price-v2"),),
        "finance_quant.lab.demo:weighted_signal",
        model_config_json=json.dumps({"weights": {"price": 1.0}}),
    )
    batch = ExperimentBatchSpec(
        "manifest-guard",
        "code",
        "env",
        "data",
        "wfo",
        "cost",
        (1,),
        "1d",
        (arm,),
    )
    with pytest.raises(LabError, match="snapshot missing arm components"):
        run_batch(batch, (snapshot,), (CanonicalOutcome("AAA", t0, t1, "1d", 0.01),))
