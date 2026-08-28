from __future__ import annotations

import json

import pytest

from finance_quant.lab.cli import load_candidates
from finance_quant.lab.core import LabError
from finance_quant.lab.matrix import expand_arm_matrix


def matrix(max_arms=100):
    return {
        "base_components": [{"lane": "price", "artifact_hash": "price-v1"}],
        "variant_lanes": {
            "news": [
                {"name": "v3", "artifact_hash": "news-v3"},
                {"name": "v4", "artifact_hash": "news-v4"},
            ],
            "kg": [
                {"name": "bounded", "artifact_hash": "kg-bounded"},
                {"name": "pathrag", "artifact_hash": "kg-pathrag"},
                {"name": "community", "artifact_hash": "kg-community"},
            ],
        },
        "combinations": [[], ["news"], ["kg"], ["news", "kg"]],
        "models": [
            {
                "name": "ridge",
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1.0, "news": 1.0, "kg": 1.0}},
            },
            {
                "name": "ridge-half-news",
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1.0, "news": 0.5, "kg": 1.0}},
            },
        ],
        "max_arms": max_arms,
        "id_prefix": "campaign-",
    }


def test_matrix_expands_requested_versions_models_and_interactions_only():
    arms = expand_arm_matrix(matrix())
    # Per model: baseline 1 + news 2 + kg 3 + news*kg 6 = 12. Two models => 24.
    assert len(arms) == 24
    assert len({arm.arm_id for arm in arms}) == 24
    by_id = {arm.arm_id: arm for arm in arms}
    interaction = by_id["campaign-ridge::kg=pathrag+news=v4"]
    assert interaction.components == (
        ("kg", "kg-pathrag"),
        ("news", "news-v4"),
        ("price", "price-v1"),
    )
    assert by_id["campaign-ridge::base"].components == (("price", "price-v1"),)


def test_matrix_refuses_unbounded_cartesian_growth():
    with pytest.raises(LabError, match="above max_arms"):
        expand_arm_matrix(matrix(max_arms=23))


def test_candidate_file_can_mix_explicit_and_matrix_arms(tmp_path):
    payload = {
        "arms": [
            {
                "arm_id": "handwritten",
                "components": [{"lane": "price", "artifact_hash": "price-v1"}],
                "executor_ref": "finance_quant.lab.demo:weighted_signal",
                "model_config": {"weights": {"price": 1.0}},
            }
        ],
        "matrix": {
            "base_components": [{"lane": "price", "artifact_hash": "price-v1"}],
            "variant_lanes": {
                "news": [{"name": "v3", "artifact_hash": "news-v3"}],
            },
            "combinations": [[], ["news"]],
            "models": [
                {
                    "name": "ridge",
                    "executor_ref": "finance_quant.lab.demo:weighted_signal",
                    "model_config": {"weights": {"price": 1.0, "news": 1.0}},
                }
            ],
            "max_arms": 10,
        },
    }
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    arms = load_candidates(path)
    assert {arm.arm_id for arm in arms} == {"handwritten", "ridge::base", "ridge::news=v3"}
