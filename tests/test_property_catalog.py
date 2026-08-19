"""Validated registry test for the property catalog (spike #8 deliverable 1).

Keeps the catalog honest: stable ids, required fields, oracle refs for any
property marked active, no dangling markdown where an oracle must be.
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "contracts" / "properties" / \
    "finance-quant-properties-v1.json"

REQUIRED = {"property_id", "statement", "tier", "severity", "owner",
            "oracle", "hidden_acceptance_required", "status"}
TIERS = {"T0", "T1", "T2", "T3", "T4"}


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
