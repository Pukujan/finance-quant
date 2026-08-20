"""Integration tests for the ontology v0.1 evidence writer (issue #6)."""
from __future__ import annotations

import pytest

from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.lineage.evidence import OntologyError
from finance_quant.lineage.pack import LocalEvidencePack
from finance_quant.lineage.writer import commit_run_evidence, evidence_reference


def _run_record(tmp_path, experiment_id: str = "B1"):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec(experiment_id, "c" * 40, "env", "snap", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"rank_ic": 0.1})
    return ledger, done


def test_writer_emits_one_evidence_commit_per_run(tmp_path):
    ledger, done = _run_record(tmp_path)
    pack = LocalEvidencePack(tmp_path / "pack")
    ref = commit_run_evidence(pack, done, "snap")
    assert ref in pack.list_hashes()
    assert len(pack.list_hashes()) == 1
    ledger.close()


def test_writer_rejects_missing_run_record(tmp_path):
    pack = LocalEvidencePack(tmp_path / "pack")
    with pytest.raises(OntologyError):
        commit_run_evidence(pack, None, "snap")


def test_writer_rejects_missing_snapshot_hash(tmp_path):
    ledger, done = _run_record(tmp_path)
    pack = LocalEvidencePack(tmp_path / "pack")
    with pytest.raises(OntologyError):
        commit_run_evidence(pack, done, "")
    ledger.close()


def test_writer_rejects_unknown_activity_type(tmp_path):
    ledger, done = _run_record(tmp_path)
    pack = LocalEvidencePack(tmp_path / "pack")
    with pytest.raises(OntologyError):
        commit_run_evidence(pack, done, "snap", activity_type="NotAnActivity")
    ledger.close()


def test_writer_allows_search_trial_activity(tmp_path):
    ledger, done = _run_record(tmp_path, experiment_id="random-v0-x")
    pack = LocalEvidencePack(tmp_path / "pack")
    ref = commit_run_evidence(pack, done, "snap", activity_type="SearchTrial")
    assert ref in pack.list_hashes()
    path = pack.root / f"{ref}.json"
    assert "SearchTrial" in path.read_text(encoding="utf-8")
    ledger.close()


def test_evidence_reference_is_hashable_and_deterministic():
    a = evidence_reference("run-1", "snap-1")
    b = evidence_reference("run-1", "snap-1")
    assert a == b
    assert a["type"] == "finance_quant_evidence_reference"
