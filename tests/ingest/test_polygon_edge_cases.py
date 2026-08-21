from __future__ import annotations

import pytest

from finance_quant.ingest.polygon import PolygonAdapter
from finance_quant.ingest.polygon_config import PolygonConfig, RateLimitSettings


def _adapter(transport):
    config = PolygonConfig(
        api_key="test-key",
        rate_limit=RateLimitSettings(
            max_retries=2, backoff_base_seconds=0, sleep_enabled=False
        ),
    )
    return PolygonAdapter(api_key="test-key", config=config, transport=transport)


def test_429_retries_with_exponential_backoff(monkeypatch):
    calls = []
    responses = [(429, {}), (429, {}), (200, {"results": []})]

    def transport(url, params, api_key):
        calls.append(url)
        return responses.pop(0)

    adapter = _adapter(transport)
    waits = []
    monkeypatch.setattr("finance_quant.ingest.polygon.time.sleep", waits.append)
    adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-02")
    assert len(calls) == 3
    assert waits == []  # disabled settings do not sleep


@pytest.mark.parametrize("status", [401, 403])
def test_auth_errors_are_clear(status):
    adapter = _adapter(lambda url, params, key: (status, {"error": "nope"}))
    with pytest.raises(RuntimeError, match=f"HTTP {status}"):
        adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-02")


def test_empty_page_is_a_valid_terminal_response():
    adapter = _adapter(lambda url, params, key: {"results": []})
    assert adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-02") == []


def test_malformed_json_is_rejected():
    adapter = _adapter(lambda url, params, key: (200, "not-json-object"))
    with pytest.raises(ValueError, match="expected a JSON object"):
        adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-02")


def test_missing_results_is_rejected():
    adapter = _adapter(lambda url, params, key: {"status": "OK"})
    with pytest.raises(ValueError, match="missing 'results'"):
        adapter.fetch_bars("AAPL", "2024-01-01", "2024-01-02")


def test_next_url_pages_are_followed_without_original_params():
    calls = []

    def transport(url, params, key):
        calls.append((url, params))
        if len(calls) == 1:
            return {
                "results": [{"t": 1704067200000, "o": 1, "h": 2, "l": 0, "c": 1, "v": 10}],
                "next_url": "https://next.example/page-2",
            }
        return {
            "results": [{"t": 1704153600000, "o": 2, "h": 3, "l": 1, "c": 2, "v": 20}],
        }

    bars = _adapter(transport).fetch_bars("AAPL", "2024-01-01", "2024-01-02")
    assert len(bars) == 2
    assert calls[1] == ("https://next.example/page-2", {})


def test_fetch_bars_mvfi_fetches_each_symbol():
    def transport(url, params, key):
        symbol = url.split("/ticker/")[1].split("/")[0]
        return {"results": [{"t": 1704067200000, "o": 1, "h": 2, "l": 0, "c": 1, "v": 10}]} 

    bars = _adapter(transport).fetch_bars_mvfi(
        ["AAPL", "MSFT"], "2024-01-01", "2024-01-02"
    )
    assert [bar["instrument_id"] for bar in bars] == ["AAPL", "MSFT"]
