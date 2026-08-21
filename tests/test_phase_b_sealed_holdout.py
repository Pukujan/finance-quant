"""Clean-runner verification for the Phase B feature-only holdout commitment."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from finance_quant.acceptance.seal import merkle_root


FIXTURE = Path("data/fixtures/phase-b-holdout")
SEAL = Path("docs/acceptance/PHASE_B_HOLDOUT_SEAL.json")


def _hash_record(line: bytes) -> str:
    return hashlib.sha256(line.rstrip(b"\n").rstrip(b"\r")).hexdigest()


def test_phase_b_holdout_merkle_root_matches_seal_without_labels():
    manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    records = FIXTURE / manifest["feature_records"]
    hashes = [_hash_record(line) for line in records.read_bytes().splitlines() if line.strip()]

    assert len(hashes) == manifest["record_count"]
    assert hashes == manifest["record_sha256"]
    assert merkle_root(hashes) == manifest["merkle_root"]
    assert seal["case_merkle_root"] == manifest["merkle_root"]
    assert "labels" not in seal
    assert "labels_hash" in seal
    assert "future_return" not in SEAL.read_text(encoding="utf-8")
