"""Local FOSSIL-shaped evidence pack: JSON files, no FOSSIL runtime required.

A dedicated pack adapter can later POST these payloads. Numeric time series stay
in the PIT store; this pack is cold-path lineage only.
"""
from __future__ import annotations

import json
from pathlib import Path

from .evidence import EvidenceCommit, evidence_payload


class LocalEvidencePack:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def commit(self, record: EvidenceCommit) -> Path:
        payload = evidence_payload(record)
        path = self.root / f"{record.hash}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_hashes(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))
