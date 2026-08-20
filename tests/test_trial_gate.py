"""Tests for Trial Gate V0 (issue #8: property-catalog CI trial gate)."""
from __future__ import annotations

import json

import pytest

from finance_quant.gate import REQUIRED_FIELDS, GateResult, check_trial_artifact, check_trial_artifact_file


def _valid_artifact(**overrides) -> dict:
    base = {
        "run_id": "a" * 64,
        "experiment_id": "B1",
        "dataset_manifest_hash": "b" * 64,
        "feature_ir_hash": "c" * 64,
        "model_config_hash": "d" * 64,
        "code_sha": "e" * 64,
        "env_lock_hash": "f" * 64,
        "seeds": [42],
        "split_policy_ref": "walk-forward-v0",
        "cost_model_ref": "cost-v0",
        "agent_origin": "human",
        "status": "success",
        "artifacts": {"model": "0" * 64, "predictions": "1" * 64},
        "metrics": {"rank_ic": 0.05},
    }
    base.update(overrides)
    return base


def test_valid_artifact_passes():
    result = check_trial_artifact(_valid_artifact())
    assert result.ok
    assert result.violations == []


def test_missing_required_fields_are_reported():
    artifact = _valid_artifact()
    for field in REQUIRED_FIELDS:
        artifact.pop(field)
    result = check_trial_artifact(artifact)
    assert not result.ok
    assert "missing required fields" in result.violations[0]
    for field in REQUIRED_FIELDS:
        assert field in result.violations[0]


def test_non_hex_hash_is_rejected():
    result = check_trial_artifact(_valid_artifact(code_sha="not-hex"))
    assert not result.ok
    assert any("code_sha" in v and "hex" in v for v in result.violations)


def test_short_hash_is_rejected():
    result = check_trial_artifact(_valid_artifact(feature_ir_hash="c" * 63))
    assert not result.ok
    assert any("feature_ir_hash" in v for v in result.violations)


def test_empty_seeds_rejected():
    result = check_trial_artifact(_valid_artifact(seeds=[]))
    assert not result.ok
    assert any("seeds" in v for v in result.violations)


def test_non_int_seeds_rejected():
    result = check_trial_artifact(_valid_artifact(seeds=["42"]))
    assert not result.ok
    assert any("seeds" in v for v in result.violations)


def test_non_terminal_status_rejected():
    result = check_trial_artifact(_valid_artifact(status="running"))
    assert not result.ok
    assert any("status" in v for v in result.violations)


def test_artifact_values_must_be_hashes():
    result = check_trial_artifact(_valid_artifact(artifacts={"model": "path/to/model"}))
    assert not result.ok
    assert any("model" in v and "hex" in v for v in result.violations)


def test_label_or_target_in_feature_hash_rejected():
    result = check_trial_artifact(_valid_artifact(feature_ir_hash="target" + "c" * 60))
    assert not result.ok
    assert any("label" in v.lower() or "target" in v.lower() for v in result.violations)


def test_contamination_sentinel_rejects_implausible_sealed_delta():
    result = check_trial_artifact(_valid_artifact(metrics={"sealed_score": 1.0, "unsealed_score": 0.1}))
    assert not result.ok
    assert any("contamination" in v.lower() for v in result.violations)


def test_contamination_sentinel_allows_skipped_check():
    result = check_trial_artifact(_valid_artifact(
        metrics={"sealed_score": 1.0, "unsealed_score": 0.1},
        skipped_contamination_check=True,
    ))
    assert result.ok


def test_trial_gate_cli_accepts_valid_file(tmp_path):
    path = tmp_path / "valid.json"
    path.write_text(json.dumps(_valid_artifact()), encoding="utf-8")
    result = check_trial_artifact_file(path)
    assert result.ok


def test_trial_gate_cli_rejects_missing_file(tmp_path):
    result = check_trial_artifact_file(tmp_path / "nope.json")
    assert not result.ok
    assert "not found" in result.violations[0].lower()


def test_trial_gate_cli_rejects_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    result = check_trial_artifact_file(path)
    assert not result.ok
    assert "JSON" in result.violations[0]
