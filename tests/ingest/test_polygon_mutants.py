from __future__ import annotations

import hashlib
import json
import sys
import types
from datetime import datetime, timezone

import pytest

from finance_quant.ingest.polygon import (
    _coerce_transport,
    _parse_date,
    snapshot_pin,
)


def test_snapshot_pin_sorts_keys_before_serializing():
    records = [{"z": 1, "a": 2}]
    blob = '{"a":2,"z":1}'
    expected = hashlib.sha256(len(blob).to_bytes(8, "big") + blob.encode()).hexdigest()
    assert snapshot_pin(records) == expected


def test_snapshot_pin_length_prefix_disambiguates_record_boundaries():
    assert snapshot_pin([{"a": "xy"}]) != snapshot_pin([{"a": "x"}, {"a": "y"}])


def test_snapshot_pin_uses_default_string_serializer_for_non_json_values():
    value = datetime(2024, 1, 2, tzinfo=timezone.utc)
    blob = json.dumps({"when": value}, sort_keys=True, separators=(",", ":"), default=str)
    expected = hashlib.sha256(len(blob).to_bytes(8, "big") + blob.encode()).hexdigest()
    assert snapshot_pin([{"when": value}]) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2024-01-02T03:04:05Z", datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)),
        ("2024-01-02T03:04:05+02:00", datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)),
    ],
)
def test_parse_date_iso_timestamp_preserves_or_parses_timezone(value, expected):
    parsed = _parse_date(value)
    if value.endswith("+02:00"):
        assert parsed.utcoffset().total_seconds() == 7200
    else:
        assert parsed == expected


def test_parse_date_rejects_unsupported_types():
    with pytest.raises(ValueError, match="unsupported date value"):
        _parse_date(None)  # type: ignore[arg-type]


def test_coerce_transport_keeps_injected_callable():
    supplied = lambda url, params, key: {"url": url, "params": params, "key": key}
    assert _coerce_transport(supplied, "https://ignored", 1) is supplied


def test_coerce_transport_real_transport_passes_key_and_timeout(monkeypatch):
    calls = []

    class Response:
        def raise_for_status(self):
            calls.append("raised")

        def json(self):
            return {"results": [1]}

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(get=get))
    transport = _coerce_transport(None, "https://base", 7.5)
    assert transport("https://endpoint", {"limit": 2}, "secret") == {"results": [1]}
    assert calls[0] == (
        "https://endpoint",
        {"params": {"limit": 2, "apiKey": "secret"}, "timeout": 7.5},
    )
    assert calls[1] == "raised"
