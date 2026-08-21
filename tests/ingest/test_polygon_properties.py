"""Hypothesis property-based tests for finance_quant.ingest.polygon module.

Covers:
- snapshot_pin determinism (same input yields same hash across repeated calls)
- snapshot_pin parsing round-trips (canonical JSON serialisation + hex digest
  always produces a stable 64-char string)
- transport call counts (each logical fetch invokes the transport exactly as
  many times as there are pages in the stubbed response, including one call
  per sub-endpoint).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import pytest
from hypothesis import given, settings, strategies as st

from finance_quant.ingest.polygon import PolygonAdapter, snapshot_pin

# ── strategy helpers ───────────────────────────────────────────────────────

_recs = st.lists(st.dictionaries(st.text(alphabet=st.characters(max_codepoint=0xA0), max_size=8), st.integers(min_value=-1e18, max_value=1e18), min_size=0, max_size=4), min_size=0, max_size=5)


# ── snapshot_pin determinism ──────────────────────────────────────────────

@given(_recs)
@settings(max_examples=30)
def test_snapshot_pin_deterministic_for_all_records(recs):
    """Two calls to snapshot_pin with identical records must produce an identical
    SHA-256 hex digest."""
    h1 = snapshot_pin(recs)
    h2 = snapshot_pin(recs)
    assert h1 == h2


@given(_recs)
@settings(max_examples=20)
def test_snapshot_pin_order_matters(recs):
    """Shuffling two elements in the record list changes the hash."""
    if len(recs) < 2:
        pytest.skip("Need at least 2 records to shuffle")
    modified = list(recs)
    # swap first two
    modified[0], modified[1] = modified[1], modified[0]
    h_original = snapshot_pin(recs)
    h_swapped = snapshot_pin(modified)
    assert h_original != h_swapped


# ── snapshot_pin round-trip / structural properties ───────────────────────

@given(_recs)
@settings(max_examples=30)
def test_snapshot_pin_returns_64_char_hex(recs):
    """The result is always 64-character lowercase hex (SHA-256 digest)."""
    h = snapshot_pin(recs)
    assert isinstance(h, str)
    assert len(h) == 64
    int(h, 16)           # will raise ValueError for bad hex


@given(_recs)
@settings(max_examples=20)
def test_snapshot_pin_unique_for_different_inputs(recs):
    """Different record lists produce different hashes (collision resistance,
    weak but practical over small domains)."""
    if not recs:
        pytest.skip("Empty-only domain trivially collides on self")
    # modify last record
    modified = list(recs)
    entry = {**modified[-1]}
    entry["_mutated"] = True
    modified[-1] = entry
    h_orig = snapshot_pin(recs)
    h_mut = snapshot_pin(modified)
    assert h_orig != h_mut


@given(_recs)
@settings(max_examples=20)
def test_snapshot_pin_matches_manual_hash(recs):
    """For non-empty inputs, the function's output equals what we'd get by
    manually doing the same canonical serialisation + length-prefix + SHA-256."""
    h_fn = snapshot_pin(recs)

    # manual computation
    h = hashlib.sha256()
    for rec in recs:
        blob = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
        h.update(len(blob).to_bytes(8, "big"))
        h.update(blob.encode("utf-8"))
    assert h_fn == h.hexdigest()


@given(_recs)
@settings(max_examples=20)
def test_snapshot_pin_empty_produces_sha256_of_nothing(recs):
    """Even though the randomiser rarely emits [], verify once explicitly that
    empty-list hashing matches hashlib.sha256().hexdigest()."""
    if recs:
        pytest.skip("only meaningful for []")
    expected = hashlib.sha256().hexdigest()
    assert snapshot_pin([]) == expected


# ── _parse_date round-trips ───────────────────────────────────────────────

# Re-import for _parse_date which isn't exported in __all__
from finance_quant.ingest.polygon import _parse_date, _iso, _to_utc_ms


@given(st.integers(min_value=int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()) * 1000,
                  max_value=int(datetime(2030, 12, 31, tzinfo=timezone.utc).timestamp()) * 1000))
@settings(max_examples=40)
def test_parse_date_epoch_ms_round_trip(ms_val):
    """An epoch-millisecond integer parsed by _parse_date then converted by
    _iso should be a valid ISO string that converts back to the same instant."""
    dt = _parse_date(ms_val)
    assert dt.tzinfo is not None, "Parse date must return timezone-aware"
    iso_str = _iso(dt)
    dt2 = datetime.fromisoformat(iso_str.replace("+00:00", "+00:00"))
    assert abs((dt2 - dt).total_seconds()) < 1


@given(st.text(min_size=4, max_size=10, alphabet="0123456789"))
@settings(max_examples=40)
def test_parse_date_digit_string_round_trip(digit_str):
    """A pure-digit string is treated as ms since epoch and parses successfully."""
    try:
        dt = _parse_date(digit_str)
        assert dt.tzinfo is not None
    except Exception:
        pytest.fail(f"_parse_date failed on digit string {digit_str!r}")


@given(st.just("2024-01-02"), st.just("2024-06-15T12:30:00Z"))
@settings(max_examples=2)
def test_parse_date_iso_strings(date_a, date_b):
    """ISO date strings parse without raising and return timezone-aware datetimes."""
    for s in (date_a, date_b):
        dt = _parse_date(s)
        assert dt.tzinfo is not None


# ── transport call counts ─────────────────────────────────────────────────

@pytest.mark.parametrize("n_pages", [0, 1, 2, 3])
def test_transport_called_once_per_page_single_bar(n_pages):
    """:meth:`PolygonAdapter.fetch_bars` always performs **at least one**
    transport call per endpoint (even when there are zero pages).  Subsequent
    calls happen only when ``next_url`` chaining tells the loop to continue.

    Expected calls:
      - n_pages == 0 → 1 call (probe returned empty)
      - n_pages >  0 → n_pages calls (each page was returned via next_url)
    """
    # Each element represents ONE transport-response roundtrip.
    # We emit a *flat list of responses* — index i is what the i-th call sees.
    bar_rows_needed = n_pages  # total rows spread across pages
    responses: list[dict] = []
    for i in range(max(n_pages, 1)):
        has_next = i < n_pages - 1 and n_pages >= 1
        resp: dict[str, Any] = {"results": []}
        if i < bar_rows_needed:
            resp["results"] = [{"t": 1704067200000, "o": 100, "h": 105, "l": 99, "c": 103, "v": 100, "vw": 100, "n": 1}]
        elif i == bar_rows_needed:
            pass  # extra probe returning empty
        if has_next:
            resp["next_url"] = f"http://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-31?page={i + 1}"
        responses.append(resp)

    call_i = 0

    def counting_transport(url, params, key):
        nonlocal call_i
        call_i += 1
        idx = call_i - 1
        if idx < len(responses):
            return responses[idx]
        return {"results": []}

    adapter = PolygonAdapter(api_key="k", transport=counting_transport)
    result = adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    expected_calls = max(n_pages, 1)
    assert call_i == expected_calls, f"Expected {expected_calls} transport calls for n_pages={n_pages}, got {call_i}"
    assert len(result) == bar_rows_needed


@pytest.mark.parametrize("n_pages_div", [0, 1, 2])
@pytest.mark.parametrize("n_pages_split", [0, 1, 2])
def test_transport_call_counts_corporate_actions(n_pages_div, n_pages_split):
    """:meth:`PolygonAdapter.fetch_corporate_actions` hits **two** sub-endpoints
    (dividends + splits). Each endpoint does at least one call.

    Total calls = ``max(n_pages_div, 1) + max(n_pages_split, 1)``.
    """
    # Build per-endpoint response sequences.
    # Note: next_url MUST still match /dividends or /splits so the transport
    # dispatch lands in the right branch on subsequent pagination round-trips.
    def _page_url(endpoint_name, i):
        return f"http://api.polygon.io/v3/reference/{endpoint_name}?page={i}"

    div_responses: list[dict] = []
    for i in range(max(n_pages_div, 1)):
        row = [{"ex_dividend_date": 1704067200000, "cash_amount": 0.72,
                "declaration_date": "2024-01-01", "record_date": "2024-01-02",
                "pay_date": "2024-01-15", "frequency": "quarterly"}] if i < n_pages_div else []
        resp: dict[str, Any] = {"results": row}
        if i < n_pages_div - 1 and n_pages_div >= 1:
            resp["next_url"] = _page_url("dividends", i + 1)
        div_responses.append(resp)

    split_responses: list[dict] = []
    for i in range(max(n_pages_split, 1)):
        row = [{"execution_date": 1718409600000, "split_from": "1", "split_to": "4"}] if i < n_pages_split else []
        resp: dict[str, Any] = {"results": row}
        if i < n_pages_split - 1 and n_pages_split >= 1:
            resp["next_url"] = _page_url("splits", i + 1)
        split_responses.append(resp)

    counts = {"div": 0, "split": 0}

    def counting_transport(url, params, key):
        if "/dividends" in url:
            counts["div"] += 1
            idx = counts["div"] - 1
            return div_responses[min(idx, len(div_responses) - 1)]
        if "/splits" in url:
            counts["split"] += 1
            idx = counts["split"] - 1
            return split_responses[min(idx, len(split_responses) - 1)]
        return {"results": []}

    adapter = PolygonAdapter(api_key="k", transport=counting_transport)
    result = adapter.fetch_corporate_actions("AAPL", "2024-01-01", "2024-12-31")

    exp_div = max(n_pages_div, 1)
    exp_split = max(n_pages_split, 1)
    assert counts["div"] == exp_div, f"div={exp_div} vs actual={counts['div']}"
    assert counts["split"] == exp_split, f"split={exp_split} vs actual={counts['split']}"
    total_expected = n_pages_div + n_pages_split
    assert len(result) == total_expected, f"records: {total_expected} vs {len(result)}"


@given(st.sampled_from(["bar", "corporate_action"]))
@settings(max_examples=3, deadline=1000)
def test_fetch_returns_consistent_namespace(namespace):
    """Every record emitted by any fetch method carries the correct namespace."""

    def bar_only_transport(url, params, key):
        if "aggs" in url:
            return {"results": [{"t": 1704067200000, "o": 100, "h": 105, "l": 99, "c": 103, "v": 100, "vw": 100, "n": 1}]}
        return {"results": []}

    def coaction_ok_transport(url, params, key):
        if "aggs" in url:
            return {"results": [{"t": 1704067200000, "o": 100, "h": 105, "l": 99, "c": 103, "v": 100, "vw": 100, "n": 1}]}
        if "dividends" in url:
            return {"results": [{"ex_dividend_date": 1704067200000, "cash_amount": 0.72,
                                 "declaration_date": "2024-01-01", "record_date": "2024-01-02",
                                 "pay_date": "2024-01-15", "frequency": "quarterly"}]}
        if "splits" in url:
            return {"results": [{"execution_date": 1718409600000, "split_from": "1", "split_to": "4"}]}
        return {"results": []}

    adapter = PolygonAdapter(api_key="x", transport=bar_only_transport)
    if namespace == "bar":
        recs = adapter.fetch_bars("X", "2024-01-01", "2024-01-31")
    else:
        adapter_ca = PolygonAdapter(api_key="x", transport=coaction_ok_transport)
        recs = adapter_ca.fetch_corporate_actions("X", "2024-01-01", "2024-12-31")

    # Empty results still satisfy the property vacuously
    for r in recs:
        assert r["namespace"] == namespace
