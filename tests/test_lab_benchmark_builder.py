from __future__ import annotations

import json

import pytest

from finance_quant.lab.benchmark import OBSERVATION_SCHEMA, assemble_benchmark, read_temporal_observations
from finance_quant.lab.cli import main as lab_main
from finance_quant.lab.core import ComponentSpec, LabError
from finance_quant.lab.registry import ComponentRegistry


T0 = "2024-01-02T16:00:00+00:00"
T1 = "2024-01-03T16:00:00+00:00"
T2 = "2024-01-04T16:00:00+00:00"


def spec(lane: str, version: str) -> ComponentSpec:
    return ComponentSpec(
        lane=lane,
        name=f"{lane}-component",
        version=version,
        code_sha="code-sha",
        input_dataset_manifest_hash="dataset-sha",
    )


def payload(*observations):
    return {"schema": OBSERVATION_SCHEMA, "observations": list(observations)}


def evaluation():
    return {
        "experiment": {
            "experiment_id": "assembled-test",
            "code_sha": "control-plane-code",
            "env_lock_hash": "env",
            "dataset_manifest_hash": "fixed-evaluation-data",
            "split_policy_ref": "wfo",
            "cost_model_ref": "2bps",
            "seeds": [1],
            "outcome_horizon": "1d",
        },
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


def test_registered_component_versions_assemble_into_one_pit_snapshot(tmp_path):
    registry = ComponentRegistry(tmp_path / "registry")
    try:
        price = registry.build(
            spec("price", "v1"),
            payload({"entity": "AAA", "known_at": T0, "payload": {"signal": 0.01}}),
        )
        news_v3 = registry.build(
            spec("news", "v3"),
            payload(
                {"entity": "AAA", "known_at": T0, "payload": {"signal": 0.02}},
                {"entity": "AAA", "known_at": T2, "payload": {"signal": 999.0}},
            ),
        )
        news_v4 = registry.build(
            spec("news", "v4"),
            payload({"entity": "AAA", "known_at": T0, "payload": {"signal": -0.015}}),
        )
        macro = registry.build(
            spec("macro", "v1"),
            payload({"entity": "*", "known_at": T0, "payload": {"signal": 0.005}}),
        )

        benchmark = assemble_benchmark(
            evaluation(),
            registry,
            (price.artifact_hash, news_v3.artifact_hash, news_v4.artifact_hash, macro.artifact_hash),
        )
        snapshot = benchmark["snapshots"][0]
        by_key = {(row["lane"], row["artifact_hash"]): row["payload"] for row in snapshot["data"]}
        assert by_key[("price", price.artifact_hash)] == {"signal": 0.01}
        assert by_key[("news", news_v3.artifact_hash)] == {"signal": 0.02}
        assert by_key[("news", news_v4.artifact_hash)] == {"signal": -0.015}
        assert by_key[("macro", macro.artifact_hash)] == {"signal": 0.005}
        assert all(row["payload"].get("signal") != 999.0 for row in snapshot["data"])
    finally:
        registry.close()


def test_component_temporal_payload_schema_is_fail_closed(tmp_path):
    registry = ComponentRegistry(tmp_path / "registry")
    try:
        artifact = registry.build(spec("news", "broken"), {"observations": []})
        with pytest.raises(LabError, match="must use schema"):
            read_temporal_observations(registry, artifact.artifact_hash)
    finally:
        registry.close()


def test_public_cli_can_publish_assemble_and_run_versioned_arms_without_handwritten_snapshots(tmp_path, capsys):
    registry = tmp_path / "registry"
    state = tmp_path / "state"

    artifacts = {}
    component_inputs = {
        "price-v1": (
            {
                "lane": "price",
                "name": "price-component",
                "version": "v1",
                "code_sha": "price-code",
                "input_dataset_manifest_hash": "price-data",
            },
            payload({"entity": "AAA", "known_at": T0, "payload": {"signal": 0.01}}),
        ),
        "news-v3": (
            {
                "lane": "news",
                "name": "news-component",
                "version": "v3",
                "code_sha": "news-code-v3",
                "input_dataset_manifest_hash": "news-data",
            },
            payload({"entity": "AAA", "known_at": T0, "payload": {"signal": 0.02}}),
        ),
        "news-v4": (
            {
                "lane": "news",
                "name": "news-component",
                "version": "v4",
                "code_sha": "news-code-v4",
                "input_dataset_manifest_hash": "news-data",
            },
            payload(
                {"entity": "AAA", "known_at": T0, "payload": {"signal": -0.015}},
                {"entity": "AAA", "known_at": T2, "payload": {"signal": 999.0}},
            ),
        ),
    }

    for name, (raw_spec, raw_payload) in component_inputs.items():
        spec_path = tmp_path / f"{name}-spec.json"
        payload_path = tmp_path / f"{name}-payload.json"
        receipt_path = tmp_path / f"{name}-artifact.json"
        spec_path.write_text(json.dumps(raw_spec), encoding="utf-8")
        payload_path.write_text(json.dumps(raw_payload), encoding="utf-8")
        assert lab_main([
            "publish-component",
            str(spec_path),
            str(payload_path),
            "--registry",
            str(registry),
            "--output",
            str(receipt_path),
        ]) == 0
        capsys.readouterr()
        artifacts[name] = json.loads(receipt_path.read_text(encoding="utf-8"))["artifact_hash"]

    evaluation_path = tmp_path / "evaluation.json"
    components_path = tmp_path / "components.json"
    benchmark_path = tmp_path / "benchmark.json"
    evaluation_path.write_text(json.dumps(evaluation()), encoding="utf-8")
    components_path.write_text(json.dumps({"artifacts": list(artifacts.values())}), encoding="utf-8")
    assert lab_main([
        "assemble-benchmark",
        str(evaluation_path),
        str(components_path),
        "--registry",
        str(registry),
        "--output",
        str(benchmark_path),
    ]) == 0
    capsys.readouterr()

    candidates = {
        "arms": [
            {
                "arm_id": "news-v3",
                "components": [
                    {"lane": "price", "artifact_hash": artifacts["price-v1"]},
                    {"lane": "news", "artifact_hash": artifacts["news-v3"]},
                ],
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1.0, "news": 1.0}},
            },
            {
                "arm_id": "news-v4",
                "components": [
                    {"lane": "price", "artifact_hash": artifacts["price-v1"]},
                    {"lane": "news", "artifact_hash": artifacts["news-v4"]},
                ],
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1.0, "news": 1.0}},
            },
        ]
    }
    candidates_path = tmp_path / "candidates.json"
    result_path = tmp_path / "result.json"
    candidates_path.write_text(json.dumps(candidates), encoding="utf-8")
    assert lab_main([
        "run",
        str(benchmark_path),
        str(candidates_path),
        "--state-dir",
        str(state),
        "--parallel",
        "2",
        "--output",
        str(result_path),
    ]) == 0
    capsys.readouterr()

    result = json.loads(result_path.read_text(encoding="utf-8"))
    predictions = {row["arm_id"]: row["predicted_return"] for row in result["predictions"]}
    assert predictions == pytest.approx({"news-v3": 0.03, "news-v4": -0.005})
    assert len({row["outcome_id"] for row in result["scores"]}) == 1
