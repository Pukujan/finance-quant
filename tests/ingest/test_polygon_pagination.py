"""Tests for pagination, rate-limit, and backoff helpers in the Polygon adapter.

Multi-page responses are simulated by recording every transport call and
returning distinct ``results``/``next_url`` payloads from a small queue.
"""
from __future__ import annotations

import time

import pytest

from finance_quant.ingest.polygon import (
    PolygonAdapter,
    _backoff_seconds,
)
from finance_quant.ingest.polygon_config import RateLimitSettings


# --------------------------------------------------------------------- helpers


def _page(*rows, next_url=None):
    return {"results": list(rows), "next_url": next_url}


def _bar(t_ms, c):
    return {"t": t_ms, "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 100, "vw": c, "n": 1}


def _div(date_ms, amount=0.5):
    return {
        "ex_dividend_date": date_ms,
        "cash_amount": amount,
        "currency": "USD",
        "declaration_date": "2024-01-01",
        "record_date": "2024-01-02",
        "pay_date": "2024-01-15",
        "frequency": "quarterly",
    }


def _split(date_ms, f="1", t="2"):
    return {"execution_date": date_ms, "split_from": f, "split_to": t}


# --------------------------------------------------------------------- pagination: bars


def test_fetch_bars_walks_next_url_until_exhausted():
    page1 = _page(
        _bar(1704067200000, 100), _bar(1704153600000, 101),
        next_url="https://api.polygon.io/v2/aggs/page2",
    )
    page2 = _page(
        _bar(1704240000000, 102), _bar(1704326400000, 103),
        next_url="https://api.polygon.io/v2/aggs/page3",
    )
    page3 = _page(_bar(1704412800000, 104))

    queue = [page1, page2, page3]
    calls: list[tuple[str, dict]] = []

    def transport(url, params, api_key):
        calls.append((url, dict(params)))
        return queue.pop(0)

    a = PolygonAdapter(
        api_key="k",
        transport=transport,
        config=None,
    )
    # Disable throttling for speed.
    a.config.rate_limit.sleep_enabled = False

    bars = a.fetch_bars("AAPL", "2024-01-01", "2024-01-05")
    assert len(bars) == 5
    assert [b["payload"]["close"] for b in bars] == [100, 101, 102, 103, 104]
    assert len(calls) == 3


def test_fetch_bars_single_page_no_next_url():
    """Backward compat: a single-page response triggers exactly one call."""
    calls: list = []

    def transport(url, params, api_key):
        calls.append(url)
        return {"results": [_bar(1704067200000, 100)]}

    a = PolygonAdapter(api_key="k", transport=transport)
    a.config.rate_limit.sleep_enabled = False
    bars = a.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    assert len(bars) == 1
    assert len(calls) == 1


def test_fetch_bars_passes_empty_params_on_followup_pages():
    """After a next_url, the adapter should not re-send the original params."""
    page1 = _page(_bar(1704067200000, 100), next_url="https://api.polygon.io/v2/aggs/page2")
    page2 = _page(_bar(1704153600000, 101))

    queue = [page1, page2]
    call_params: list[dict] = []

    def transport(url, params, api_key):
        call_params.append(dict(params))
        return queue.pop(0)

    a = PolygonAdapter(api_key="k", transport=transport)
    a.config.rate_limit.sleep_enabled = False
    a.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    assert "limit" in call_params[0] or "adjusted" in call_params[0]
    # The followup call should be an empty params dict (the next_url
    # already encodes the cursor).
    assert call_params[1] == {}


# --------------------------------------------------------------------- pagination: corporate actions


def test_fetch_corporate_actions_paginates_dividends_and_splits():
    div_p1 = _page(_div(1704067200000, 0.10), next_url="https://api.polygon.io/v3/reference/dividends?cursor=2")
    div_p2 = _page(_div(1706659200000, 0.11))
    split_p1 = _page(_split(1704067200000, "1", "4"), next_url="https://api.polygon.io/v3/reference/splits?cursor=2")
    split_p2 = _page(_split(1706659200000, "1", "5"), next_url="https://api.polygon.io/v3/reference/splits?cursor=3")
    split_p3 = _page(_split(1709251200000, "1", "6"))

    queue = [div_p1, div_p2, split_p1, split_p2, split_p3]
    calls: list[str] = []

    def transport(url, params, api_key):
        calls.append(url)
        return queue.pop(0)

    a = PolygonAdapter(api_key="k", transport=transport)
    a.config.rate_limit.sleep_enabled = False
    actions = a.fetch_corporate_actions("AAPL", "2024-01-01", "2024-12-31")

    divs = [r for r in actions if r["payload"]["kind"] == "dividend"]
    splits = [r for r in actions if r["payload"]["kind"] == "split"]
    assert len(divs) == 2
    assert len(splits) == 3
    assert len(calls) == 5  # 2 dividend pages + 3 split pages


# --------------------------------------------------------------------- rate-limit helper


def test_throttle_sleeps_when_enabled(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("finance_quant.ingest.polygon.time.sleep", lambda s: sleeps.append(s))

    a = PolygonAdapter(
        api_key="k",
        transport=lambda u, p, k: {"results": []},
        config=None,
    )
    a.config.rate_limit.requests_per_second = 10.0
    a.config.rate_limit.sleep_enabled = True
    a._throttle()
    assert len(sleeps) == 1
    assert abs(sleeps[0] - 0.1) < 1e-9


def test_throttle_noop_when_disabled(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr("finance_quant.ingest.polygon.time.sleep", lambda s: sleeps.append(s))

    a = PolygonAdapter(api_key="k", transport=lambda u, p, k: {"results": []})
    a.config.rate_limit.sleep_enabled = False
    a._throttle()
    assert sleeps == []


def test_throttle_called_once_per_page(monkeypatch):
    """A multi-page fetch should call _throttle once per page request."""
    page1 = _page(_bar(1704067200000, 100), next_url="https://api.polygon.io/page2")
    page2 = _page(_bar(1704153600000, 101))
    queue = [page1, page2]

    sleeps: list[float] = []
    monkeypatch.setattr("finance_quant.ingest.polygon.time.sleep", lambda s: sleeps.append(s))

    a = PolygonAdapter(
        api_key="k",
        transport=lambda u, p, k: queue.pop(0),
    )
    a.config.rate_limit.requests_per_second = 100.0
    a.config.rate_limit.sleep_enabled = True
    a.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    assert len(sleeps) == 2


# --------------------------------------------------------------------- backoff helper


def test_backoff_seconds_exponential_growth():
    s = RateLimitSettings(backoff_base_seconds=1.0, max_retries=4, requests_per_second=5)
    assert _backoff_seconds(1, s) == 1.0
    assert _backoff_seconds(2, s) == 2.0
    assert _backoff_seconds(3, s) == 4.0
    assert _backoff_seconds(4, s) == 8.0


def test_backoff_seconds_zero_for_invalid_attempt():
    s = RateLimitSettings()
    assert _backoff_seconds(0, s) == 0.0
    assert _backoff_seconds(-1, s) == 0.0


def test_backoff_respects_custom_base():
    s = RateLimitSettings(backoff_base_seconds=0.5, max_retries=3, requests_per_second=5)
    assert _backoff_seconds(1, s) == 0.5
    assert _backoff_seconds(2, s) == 1.0
    assert _backoff_seconds(3, s) == 2.0


# --------------------------------------------------------------------- revision/source from config


def test_revision_and_source_carried_through_paginated_records():
    page1 = _page(_bar(1704067200000, 100), next_url="https://api.polygon.io/p2")
    page2 = _page(_bar(1704153600000, 101))
    queue = [page1, page2]

    a = PolygonAdapter(
        api_key="k",
        transport=lambda u, p, k: queue.pop(0),
        revision=9,
        source="src-X",
    )
    a.config.rate_limit.sleep_enabled = False
    bars = a.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    for b in bars:
        assert b["revision"] == 9
        assert b["source"] == "src-X"
        assert b["superseded_by"] is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
