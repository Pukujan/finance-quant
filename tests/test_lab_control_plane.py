from __future__ import annotations

import json

import pytest
from hypothesis import given, strategies as st

from finance_quant.experiments.ledger import ExperimentLedger
from finance_quant.lab.cli import main as lab_main
from finance_quant.lab.core import (
    ArmScore,
    ArmSpec,
    CanonicalOutcome,
    ComponentSpec,
    ExperimentBatchSpec,
    KnowledgeManifest,
    LabError,
    TemporalLaneDatum,
    freeze_snapshot,
)
from finance_quant.lab.registry import ComponentRegistry
from finance_quant.lab.runner import router_weights, run_batch, run_spec_for


T0 = "2024-01-02T16:00:00+00:00"
T1 = "2024-01-03T16:00:00+00:00"
T2 = "2024-01-04T16:00:00+00:00"


def component(lane: str, version: str, *, parents=(), params=None) -> ComponentSpec:
    return ComponentSpec(
        lane=lane,
        name=f"{lane}-extractor",
        version=version,
        code_sha="code-1",
        input_dataset_manifest_hash="dataset-1",
        parameters_json=json.dumps(params or {}),
        parent_artifact_hashes=tuple(parents),
    )


def arm_specs():
    price_manifest = KnowledgeManifest((("price", "price-v1"),)).manifest_hash
    knowledge_manifest = KnowledgeManifest((("price", "price-v1"), ("news", "news-v1"))).manifest_hash
    return (
        ArmSpec(
            "A-price",
            ("price",),
            price_manifest,
            "finance_quant.lab.demo:weighted_signal",
            model_config_json=json.dumps({"weights": {"price": 1.0}}),
        ),
        ArmSpec(
            "B-price-news",
            ("price", "news"),
            knowledge_manifest,
            "finance_quant.lab.demo:weighted_signal",
            model_config_json=json.dumps({"weights": {"price": 1.0, "news": 0.5}}),
        ),
    )


def batch(arms):
    return ExperimentBatchSpec(
        experiment_id="lab-test",
        code_sha="code-sha",
        env_lock_hash="env-hash",
        dataset_manifest_hash="dataset-hash",
        split_policy_ref="walk-forward-v1",
        cost_model_ref="cost-2bps",
        seeds=(7,),
        outcome_horizon="1d",
        arms=tuple(arms),
    )


def snapshots():
    data0 = (
        TemporalLaneDatum.from_payload("price", "price-v1", T0, {"signal": 0.01}),
        TemporalLaneDatum.from_payload("news", "news-v1", T0, {"signal": -0.002}),
    )
    data1 = (
        TemporalLaneDatum.from_payload("price", "price-v1", T1, {"signal": -0.01}),
        TemporalLaneDatum.from_payload("news", "news-v1", T1, {"signal": 0.03}),
    )
    return (
        freeze_snapshot("AAA", T0, "1d", data0),
        freeze_snapshot("AAA", T1, "1d", data1),
    )


def outcomes():
    return (
        CanonicalOutcome("AAA", T0, T1, "1d", 0.02, 2.0),
        CanonicalOutcome("AAA", T1, T2, "1d", -0.01, 2.0),
    )


def test_component_registry_is_content_addressed_immutable_and_tracks_descendants(tmp_path):
    registry = ComponentRegistry(tmp_path / "registry")
    try:
        price = registry.build(component("price", "v1"), {"rows": [1, 2, 3]})
        same = registry.build(component("price", "v1"), {"rows": [1, 2, 3]})
        assert same.artifact_hash == price.artifact_hash

        news_v1 = registry.build(component("news", "v1", parents=(price.artifact_hash,)), {"story": "a"})
        news_v2 = registry.build(component("news", "v2", parents=(price.artifact_hash,)), {"story": "b"})
        model = registry.build(component("graph_paths", "v1", parents=(news_v1.artifact_hash,)), {"paths": 2})

        before = registry.read_payload(news_v1.artifact_hash)
        assert registry.read_payload(news_v2.artifact_hash) != before
        assert registry.read_payload(news_v1.artifact_hash) == before

        descendants = set(registry.descendants((news_v1.artifact_hash,)))
        assert descendants == {model.artifact_hash}
        assert news_v2.artifact_hash not in descendants
    finally:
        registry.close()


def test_manifest_hash_is_order_independent_and_lane_unique():
    a = KnowledgeManifest((("news", "n"), ("price", "p")))
    b = KnowledgeManifest((("price", "p"), ("news", "n")))
    assert a.manifest_hash == b.manifest_hash
    with pytest.raises(LabError):
        KnowledgeManifest((("price", "p1"), ("price", "p2")))


@given(st.integers(min_value=-10_000, max_value=10_000))
def test_future_known_data_cannot_change_prior_frozen_snapshot(future_signal):
    base = (TemporalLaneDatum.from_payload("price", "p1", T0, {"signal": 1}),)
    future = TemporalLaneDatum.from_payload("price", "p2", T2, {"signal": future_signal})
    before = freeze_snapshot("AAA", T1, "1d", base)
    after = freeze_snapshot("AAA", T1, "1d", base + (future,))
    assert before.snapshot_id == after.snapshot_id


def test_snapshot_rejects_future_known_lane_if_bypassing_freeze():
    from finance_quant.lab.core import DecisionSnapshot, LaneValue

    with pytest.raises(LabError):
        DecisionSnapshot(
            "AAA",
            T0,
            "1d",
            (LaneValue("news", "n1", T1, json.dumps({"signal": 1})),),
        )


def test_arm_receives_only_declared_lanes():
    from finance_quant.lab.core import arm_context

    a, b = arm_specs()
    snapshot = snapshots()[0]
    context_a = arm_context(snapshot, a)
    context_b = arm_context(snapshot, b)
    assert [item.lane for item in context_a.lanes] == ["price"]
    assert [item.lane for item in context_b.lanes] == ["news", "price"]
    with pytest.raises(KeyError):
        context_a.lane_payload("news")


def test_parallel_and_sequential_runs_are_identical_and_share_canonical_outcomes():
    spec = batch(arm_specs())
    seq = run_batch(spec, snapshots(), outcomes(), max_workers=1)
    par = run_batch(spec, snapshots(), outcomes(), max_workers=4)
    assert seq == par
    for decision_time in (T0, T1):
        rows = [score for score in seq.scores if score.decision_time == decision_time]
        assert len({score.outcome_id for score in rows}) == 1
        assert {score.arm_id for score in rows} == {"A-price", "B-price-news"}


def test_canonical_outcome_coverage_must_be_exact():
    with pytest.raises(LabError):
        run_batch(batch(arm_specs()), snapshots(), outcomes()[:1])


def test_router_cannot_learn_from_outcome_that_has_not_resolved_yet():
    result = run_batch(batch(arm_specs()), snapshots(), outcomes())
    early = router_weights(("A-price", "B-price-news"), T1, result.scores)
    future = ArmScore(
        "B-price-news", "AAA", T1, T2, "1d", "future",
        10.0, 10.0, 0.0, 0.0, 0.0, 1.0, 100.0,
    )
    with_future = router_weights(("A-price", "B-price-news"), T1, result.scores + (future,))
    assert early == with_future


def test_lab_runs_are_idempotently_identified_in_existing_experiment_ledger(tmp_path):
    spec = batch(arm_specs())
    arm = spec.arms[0]
    run_spec = run_spec_for(spec, arm)
    assert run_spec.knowledge_manifest_hash == arm.knowledge_manifest_hash
    assert run_spec.arm_spec_hash == arm.arm_spec_hash

    ledger = ExperimentLedger(tmp_path / "ledger.sqlite")
    try:
        first = ledger.begin(run_spec)
        second = ledger.begin(run_spec)
        assert first.run_id == second.run_id

        changed = ArmSpec(
            arm.arm_id,
            arm.lanes,
            arm.knowledge_manifest_hash,
            arm.executor_ref,
            model_config_json=json.dumps({"weights": {"price": 2.0}}),
        )
        third = ledger.begin(run_spec_for(batch((changed, spec.arms[1])), changed))
        assert third.run_id != first.run_id
    finally:
        ledger.close()


def test_cli_separates_fixed_benchmark_from_candidate_arms(tmp_path, capsys):
    price_manifest = KnowledgeManifest((("price", "price-v1"),)).manifest_hash
    knowledge_manifest = KnowledgeManifest((("price", "price-v1"), ("news", "news-v1"))).manifest_hash
    benchmark = {
        "experiment": {
            "experiment_id": "cli-test",
            "code_sha": "code",
            "env_lock_hash": "env",
            "dataset_manifest_hash": "data",
            "split_policy_ref": "wfo",
            "cost_model_ref": "2bps",
            "seeds": [1],
            "outcome_horizon": "1d",
        },
        "snapshots": [
            {
                "entity": "AAA",
                "decision_time": T0,
                "horizon": "1d",
                "data": [
                    {"lane": "price", "artifact_hash": "price-v1", "known_at": T0, "payload": {"signal": 0.01}},
                    {"lane": "news", "artifact_hash": "news-v1", "known_at": T0, "payload": {"signal": 0.02}},
                    {"lane": "news", "artifact_hash": "future", "known_at": T2, "payload": {"signal": 999}},
                ],
            }
        ],
        "outcomes": [
            {
                "entity": "AAA",
                "decision_time": T0,
                "outcome_time": T1,
                "horizon": "1d",
                "realized_return": 0.01,
                "cost_bps": 2,
            }
        ],
    }
    candidates = {
        "arms": [
            {
                "arm_id": "price",
                "lanes": ["price"],
                "knowledge_manifest_hash": price_manifest,
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1}},
            },
            {
                "arm_id": "price-news",
                "lanes": ["price", "news"],
                "knowledge_manifest_hash": knowledge_manifest,
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1, "news": 1}},
            },
        ]
    }
    benchmark_path = tmp_path / "benchmark.json"
    candidate_path = tmp_path / "candidates.json"
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
    candidate_path.write_text(json.dumps(candidates), encoding="utf-8")
    rc = lab_main([
        "run", str(benchmark_path), str(candidate_path),
        "--state-dir", str(tmp_path / "state"), "--parallel", "2",
    ])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    predictions = {row["arm_id"]: row["predicted_return"] for row in result["predictions"]}
    assert predictions["price"] == pytest.approx(0.01)
    assert predictions["price-news"] == pytest.approx(0.03)


def test_candidate_file_cannot_smuggle_outcomes(tmp_path):
    from finance_quant.lab.cli import load_candidates

    path = tmp_path / "bad-candidates.json"
    path.write_text(json.dumps({"arms": [], "outcomes": [{"fake": True}]}), encoding="utf-8")
    with pytest.raises(LabError, match="cannot own benchmark data"):
        load_candidates(path)
