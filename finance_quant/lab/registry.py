"""Content-addressed immutable component registry and dependency DAG."""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from .core import ComponentArtifact, ComponentSpec, KnowledgeManifest, LabError, canonical_json, content_hash


_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS artifacts(
    artifact_hash TEXT PRIMARY KEY,
    spec_hash TEXT NOT NULL,
    lane TEXT NOT NULL,
    component_name TEXT NOT NULL,
    component_version TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_artifacts_spec ON artifacts(spec_hash);
CREATE TABLE IF NOT EXISTS artifact_edges(
    parent_hash TEXT NOT NULL,
    child_hash TEXT NOT NULL,
    PRIMARY KEY(parent_hash, child_hash)
);
"""


class ComponentRegistry:
    """Immutable local registry. Identical content/spec always resolves to one identity."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.artifact_root = self.root / "artifacts"
        self.artifact_root.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(self.root / "registry.sqlite"), check_same_thread=False)
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _payload_bytes(payload: bytes | str | Mapping[str, Any] | list[Any]) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        return canonical_json(payload).encode("utf-8")

    def build(
        self,
        spec: ComponentSpec,
        payload: bytes | str | Mapping[str, Any] | list[Any],
    ) -> ComponentArtifact:
        payload_bytes = self._payload_bytes(payload)
        payload_hash = content_hash({"bytes_hex": payload_bytes.hex()})
        artifact_hash = content_hash(
            {
                "spec_hash": spec.spec_hash,
                "payload_hash": payload_hash,
                "parents": spec.parent_artifact_hashes,
            }
        )
        directory = self.artifact_root / artifact_hash
        payload_path = directory / "payload.bin"
        metadata_path = directory / "metadata.json"
        metadata = {
            "artifact_hash": artifact_hash,
            "spec_hash": spec.spec_hash,
            "spec": asdict(spec),
            "payload_hash": payload_hash,
            "parent_artifact_hashes": list(spec.parent_artifact_hashes),
        }
        metadata_text = canonical_json(metadata)

        with self._lock:
            existing = self.get(artifact_hash)
            if existing is not None:
                if Path(existing.payload_path).read_bytes() != payload_bytes:
                    raise LabError("content-address collision or mutated artifact")
                return existing

            for parent in spec.parent_artifact_hashes:
                if self.get(parent) is None:
                    raise LabError(f"unknown parent artifact: {parent}")

            directory.mkdir(parents=True, exist_ok=True)
            self._atomic_write(payload_path, payload_bytes)
            self._atomic_write(metadata_path, metadata_text.encode("utf-8"))

            try:
                self._db.execute(
                    "INSERT INTO artifacts VALUES (?,?,?,?,?,?,?)",
                    (
                        artifact_hash,
                        spec.spec_hash,
                        spec.lane,
                        spec.name,
                        spec.version,
                        payload_hash,
                        metadata_text,
                    ),
                )
                for parent in spec.parent_artifact_hashes:
                    self._db.execute(
                        "INSERT OR IGNORE INTO artifact_edges(parent_hash, child_hash) VALUES (?,?)",
                        (parent, artifact_hash),
                    )
                self._db.commit()
            except sqlite3.IntegrityError:
                self._db.rollback()
                existing = self.get(artifact_hash)
                if existing is not None:
                    return existing
                raise
        return self.get_required(artifact_hash)

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        if path.exists():
            if path.read_bytes() != payload:
                raise LabError(f"immutable artifact path already contains different bytes: {path}")
            return
        fd, temp_name = tempfile.mkstemp(prefix=".tmp-", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def get(self, artifact_hash: str) -> ComponentArtifact | None:
        row = self._db.execute(
            "SELECT artifact_hash,spec_hash,lane,component_name,component_version,payload_hash,metadata_json "
            "FROM artifacts WHERE artifact_hash=?",
            (artifact_hash,),
        ).fetchone()
        if row is None:
            return None
        h, spec_hash, lane, name, version, payload_hash, metadata_json = row
        metadata = json.loads(metadata_json)
        directory = self.artifact_root / h
        return ComponentArtifact(
            h,
            spec_hash,
            lane,
            name,
            version,
            payload_hash,
            tuple(metadata.get("parent_artifact_hashes", ())),
            str(directory / "metadata.json"),
            str(directory / "payload.bin"),
        )

    def get_required(self, artifact_hash: str) -> ComponentArtifact:
        artifact = self.get(artifact_hash)
        if artifact is None:
            raise KeyError(artifact_hash)
        return artifact

    def read_payload(self, artifact_hash: str) -> bytes:
        return Path(self.get_required(artifact_hash).payload_path).read_bytes()

    def manifest(self, lane_to_artifact: Mapping[str, str]) -> KnowledgeManifest:
        for lane, artifact_hash in lane_to_artifact.items():
            artifact = self.get_required(artifact_hash)
            if artifact.lane != lane:
                raise LabError(f"artifact {artifact_hash} belongs to lane {artifact.lane!r}, not {lane!r}")
        return KnowledgeManifest(tuple(lane_to_artifact.items()))

    def children(self, artifact_hash: str) -> tuple[str, ...]:
        rows = self._db.execute(
            "SELECT child_hash FROM artifact_edges WHERE parent_hash=? ORDER BY child_hash",
            (artifact_hash,),
        ).fetchall()
        return tuple(row[0] for row in rows)

    def descendants(self, changed: Iterable[str]) -> tuple[str, ...]:
        queue = list(dict.fromkeys(changed))
        seen: set[str] = set()
        while queue:
            parent = queue.pop(0)
            for child in self.children(parent):
                if child not in seen:
                    seen.add(child)
                    queue.append(child)
        return tuple(sorted(seen))
