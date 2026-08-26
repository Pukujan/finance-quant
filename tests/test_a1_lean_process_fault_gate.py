from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from scripts.a1_lean_process_fault_gate import (
    run_candidate_process,
    run_fault_campaign,
    validate_persisted_evidence,
)


def test_candidate_process_success_is_not_mislabeled_as_fault() -> None:
    result = run_candidate_process(
        [sys.executable, "-c", "print('ok')"], timeout_seconds=5.0
    )
    assert result["disposition"] == "PROCESS_OK"
    assert result["fault_class"] is None
    assert result["exit_code"] == 0
    assert result["authority"] == "NONE"


def test_persisted_evidence_exact_match_required(tmp_path: Path) -> None:
    expected = {"semantic_conformance": "PASS", "authority": "NONE"}
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(expected), encoding="utf-8")
    assert validate_persisted_evidence(path, expected) == expected

    path.write_text(
        json.dumps({"semantic_conformance": "FAIL", "authority": "NONE"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not match recomputed"):
        validate_persisted_evidence(path, expected)


def test_process_fault_campaign_detects_every_injected_fault() -> None:
    receipt = run_fault_campaign()
    assert receipt["status"] == "PASS"
    assert receipt["runtime_disposition"] == "PENDING"
    assert receipt["authority"] == "NONE"
    assert receipt["sealed_holdout_access"] == "DENIED_TO_ORDINARY_AGENTS"
    assert set(receipt["fault_classes"]) == {
        "nonzero_exit",
        "timeout",
        "dependency_missing",
        "candidate_output_corruption",
        "persisted_evidence_corruption",
    }
    assert all(case["disposition"] == "FAIL_CLOSED" for case in receipt["cases"])
