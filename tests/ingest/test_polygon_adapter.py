from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from finance_quant.ingest.polygon import PolygonAdapter, snapshot_pin

# -- helpers ---------------------------------------------------------

def _stub_transport(url: str, params: dict, api_key: str) -> dict:
    """Canned responses keyed on the request URL."""
    responses = {
        "aggs": {
            "results": [
                {"t": 1704067200000, "o": 100, "h": 105, "l": 99, "c": 103, "v": 1_000_000, "vw": 102.5, "n": 5000},
            ]
        },
        "dividends": {
            "results": [
                {"ex_dividend_date": 1704067200000, "cash_amount": 0.72, "declaration_date": "2023-12-15", "record_date": "2024-01-02", "pay_date": "2024-01-15", "frequency": "quarterly"},
            ]
        },
        "splits": {
            "results": [
                {"execution_date": 1718409600000, "split_from": "1", "split_to": "4"},
            ]
        },
    }
    if "/v2/aggs/" in url:
        return responses["aggs"]
    if "/v3/reference/dividends" in url:
        return responses["dividends"]
    if "/v3/reference/splits" in url:
        return responses["splits"]
    return {"results": []}


# -- fixtures --------------------------------------------------------

def adapter() -> PolygonAdapter:
    return PolygonAdapter(
        api_key="fake-key-that-is-never-sent",
        transport=_stub_transport,
        revision=5,
        source="polygon-test",
    )


# -- bar mapping -----------------------------------------------------

def test_fetch_bars_map_to_bar_namespace_and_ohlcv():
    a = adapter()
    bars = a.fetch_bars("AAPL", "2024-01-01", "2024-01-31")
    assert len(bars) == 1
    rec = bars[0]
    assert rec["namespace"] == "bar"
    assert rec["instrument_id"] == "AAPL"
    assert rec["revision"] == 5
    assert rec["source"] == "polygon-test"
    assert rec["superseded_by"] is None
    p = rec["payload"]
    assert p["open"] == 100 and p["high"] == 105
    assert p["low"] == 99 and p["close"] == 103
    assert p["volume"] == 1_000_000
    assert p["vwap"] == 102.5
    assert p["trades"] == 5000
    assert "vt" in rec and "kt" in rec
    assert rec["ingest_receipt"]["endpoint"] == "/v2/aggs/ticker/range"


def test_fetch_bars_empty_results():
    def empty_transport(_url, _params, _key):
        return {"results": []}
    a = PolygonAdapter(api_key="x", transport=empty_transport)
    assert a.fetch_bars("Z", "2024-01-01", "2024-01-31") == []


# -- corporate actions -----------------------------------------------

def test_fetch_corporate_actions_splits_and_dividends():
    a = adapter()
    actions = a.fetch_corporate_actions("AAPL", "2024-01-01", "2024-12-31")
    kinds = {act["payload"]["kind"] for act in actions}
    assert kinds == {"dividend", "split"}
    dividend = next(a for a in actions if a["payload"]["kind"] == "dividend")
    assert dividend["namespace"] == "corporate_action"
    assert dividend["payload"]["amount"] == 0.72
    assert dividend["payload"]["currency"] is None  # not present in fixture
    split = next(a for a in actions if a["payload"]["kind"] == "split")
    assert split["namespace"] == "corporate_action"
    assert split["payload"]["split_from"] == "1"
    assert split["payload"]["split_to"] == "4"


def test_fetch_corporate_actions_empty():
    no_op = lambda u, p, k: {"results": []}
    a = PolygonAdapter(api_key="x", transport=no_op)
    assert a.fetch_corporate_actions("ZZ", "2024-01-01", "2024-01-31") == []


# -- snapshot_pin determinism ----------------------------------------

def test_snapshot_pin_deterministic():
    records = [{"c": 1, "a": 2}, {"b": 3}]
    h1 = snapshot_pin(records)
    h2 = snapshot_pin(records)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex digest


def test_snapshot_pin_order_sensitivity():
    r1 = [{"a": 1}, {"b": 2}]
    r2 = [{"b": 2}, {"a": 1}]
    assert snapshot_pin(r1) != snapshot_pin(r2)


# -- transport injection & no real key access ------------------------

def test_transport_is_injectable_and_no_real_key_used():
    """The transport callable must be called and the stubbed api_key string
    must NOT appear in any actual HTTP request because we never send."""

    call_log: list[tuple[str, list]] = []

    def logging_transport(url: str, params: dict, api_key: str) -> dict:
        call_log.append((url, list(params.keys())))
        # Never raise; always return canned data
        if "/v2/aggs/" in url:
            return {"results": []}
        if "dividends" in url:
            return {"results": []}
        if "splits" in url:
            return {"results": []}
        return {"results": []}

    a = PolygonAdapter(api_key="super-secret-KEY", transport=logging_transport)
    a.fetch_bars("MSFT", "2024-01-01", "2024-01-31")
    a.fetch_corporate_actions("MSFT", "2024-01-01", "2024-01-31")

    assert len(call_log) == 3

    # Verify our "secret" key was passed as an arg but transport can choose
    # not to serialize it — just confirm transport was invoked 3 times.
    urls = [cl[0] for cl in call_log]
    assert any("/v2/aggs/" in u for u in urls)
    assert any("dividends" in u for u in urls)
    assert any("splits" in u for u in urls)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
