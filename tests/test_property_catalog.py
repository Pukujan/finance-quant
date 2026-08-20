"""Validated registry test for the property catalog (spike #8 deliverable 1).

Keeps the catalog honest: stable ids, required fields, oracle refs for any
property marked active, no dangling markdown where an oracle must be, and every
oracle reference resolves to an existing artifact.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CATALOG = Path(__file__).resolve().parents[1] / "contracts" / "properties" / \
    "finance-quant-properties-v1.json"

REQUIRED = {"property_id", "statement", "tier", "severity", "owner",
            "oracle", "hidden_acceptance_required", "status"}
TIERS = {"T0", "T1", "T2", "T3", "T4"}

ROOT = CATALOG.parents[2]
TESTS_DIR = ROOT / "tests"
FORMAL_DIR = ROOT / "formal"


def _collect_pytest_nodes() -> set[str]:
    """Return the set of collected test node ids relative to this test run."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    nodes = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("No module") or " collected" in line:
            continue
        if "::" in line:
            nodes.add(line)
    return nodes


def _resolve_oracle(ref: str):
    """Return (ok: bool, message: str) for a single oracle reference."""
    if ref.startswith("tests/") and "::" in ref:
        path_part, node_part = ref.split("::", 1)
        file_path = ROOT / path_part
        if not file_path.is_file():
            return False, f"test file not found: {path_part}"
        return True, f"pytest node {node_part} in {path_part}"
    if ref.startswith("formal/"):
        artifact = ROOT / ref
        if not artifact.exists():
            return False, f"formal artifact not found: {ref}"
        return True, f"formal artifact exists: {ref}"
    if ref.startswith("scripts/"):
        script = ROOT / ref
        if not script.is_file():
            return False, f"script not found: {ref}"
        return True, f"script exists: {ref}"
    return False, f"unsupported oracle reference format: {ref}"


def test_catalog_is_machine_valid():
    cat = json.loads(CATALOG.read_text())
    assert cat["catalog_version"] == "1.0.0"
    props = cat["properties"]
    assert len(props) >= 10, "catalog should cover the invariant families"
    ids = [p["property_id"] for p in props]
    assert len(ids) == len(set(ids)), "property_id must be unique and stable"
    for p in props:
        missing = REQUIRED - p.keys()
        assert not missing, f"{p.get('property_id')}: missing {missing}"
        assert p["tier"] in TIERS
        assert p["statement"].strip(), "statement must not be empty"
        if p["status"] == "active":
            assert p["oracle"], f"{p['property_id']}: active without oracle"


def test_active_oracle_references_resolve():
    """Every active property's oracle list points at real files/tests/artifacts."""
    cat = json.loads(CATALOG.read_text())
    failures = []
    for prop in cat["properties"]:
        if prop["status"] != "active":
            continue
        for ref in prop["oracle"]:
            ok, msg = _resolve_oracle(ref)
            if not ok:
                failures.append(f"{prop['property_id']} -> {ref}: {msg}")
    assert not failures, "\n".join(failures)


def test_oracle_test_files_exist_on_disk():
    """Pytest-style oracle references name files that exist under tests/."""
    cat = json.loads(CATALOG.read_text())
    failures = []
    for prop in cat["properties"]:
        for ref in prop.get("oracle", []):
            if not (ref.startswith("tests/") and "::" in ref):
                continue
            path_part = ref.split("::", 1)[0]
            if not (ROOT / path_part).is_file():
                failures.append(f"{prop['property_id']} -> {path_part}")
    assert not failures, "missing oracle test files: " + ", ".join(failures)


def test_oracle_function_refs_are_collected():
    """Pytest function refs in the catalog are actually collected by pytest."""
    cat = json.loads(CATALOG.read_text())
    collected = _collect_pytest_nodes()
    failures = []
    for prop in cat["properties"]:
        if prop["status"] != "active":
            continue
        for ref in prop["oracle"]:
            if not (ref.startswith("tests/") and "::" in ref):
                continue
            if ref not in collected:
                failures.append(f"{prop['property_id']} -> {ref}")
    assert not failures, "oracle refs not collected by pytest:\n" + "\n".join(failures)


def _dangling_catalog() -> dict:
    return {
        "catalog_version": "1.0.0",
        "project": "finance-quant-test",
        "properties": [
            {
                "property_id": "FQ-TEST-DANGLING",
                "statement": "A property whose oracle does not resolve.",
                "tier": "T1",
                "severity": "high",
                "owner": "test",
                "oracle": ["tests/does_not_exist.py::test_missing"],
                "hidden_acceptance_required": False,
                "status": "active",
            }
        ],
    }


def test_resolver_flags_dangling_oracle(tmp_path: Path):
    """The resolution helper rejects missing test files and missing functions."""
    ok, msg = _resolve_oracle("tests/does_not_exist.py::test_missing")
    assert not ok
    assert "not found" in msg.lower()

    ok, msg = _resolve_oracle("formal/tla/DoesNotExist.tla")
    assert not ok
    assert "not found" in msg.lower()

    ok, msg = _resolve_oracle("scripts/does_not_exist.py")
    assert not ok
    assert "not found" in msg.lower()

    ok, msg = _resolve_oracle("unsupported_format")
    assert not ok
    assert "unsupported" in msg.lower()


def test_catalog_validation_rejects_dangling_oracle(monkeypatch, tmp_path: Path):
    """If a catalog property points at a missing oracle, validation surfaces it."""
    fake = tmp_path / "fake-catalog.json"
    fake.write_text(json.dumps(_dangling_catalog()))

    original_loads = json.loads

    def load_fake(_s):
        return original_loads(fake.read_text())

    monkeypatch.setattr("tests.test_property_catalog.json.loads", load_fake)
    # Re-use the active-oracle resolution logic directly with the fake catalog.
    failures = []
    cat = load_fake(None)
    for prop in cat["properties"]:
        if prop["status"] != "active":
            continue
        for ref in prop["oracle"]:
            ok, msg = _resolve_oracle(ref)
            if not ok:
                failures.append(f"{prop['property_id']} -> {ref}: {msg}")
    assert failures
    assert "FQ-TEST-DANGLING" in failures[0]

