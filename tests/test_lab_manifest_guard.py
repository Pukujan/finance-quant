import json

import pytest

from finance_quant.lab.core import ArmSpec, CanonicalOutcome, ExperimentBatchSpec, KnowledgeManifest, LabError, TemporalLaneDatum, freeze_snapshot
from finance_quant.lab.runner import run_batch


def test_arm_cannot_claim_a_different_knowledge_manifest():
    t0 = "2024-01-02T16:00:00+00:00"
    t1 = "2024-01-03T16:00:00+00:00"
    snapshot = freeze_snapshot(
        "AAA",
        t0,
        "1d",
        (TemporalLaneDatum.from_payload("price", "price-v1", t0, {"signal": 0.01}),),
    )
    wrong_manifest = KnowledgeManifest((("price", "price-v2"),)).manifest_hash
    arm = ArmSpec(
        "bad-manifest",
        ("price",),
        wrong_manifest,
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
    with pytest.raises(LabError, match="manifest does not match"):
        run_batch(batch, (snapshot,), (CanonicalOutcome("AAA", t0, t1, "1d", 0.01),))
