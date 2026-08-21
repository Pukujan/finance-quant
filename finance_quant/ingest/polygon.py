"""Polygon.io market data adapter for finance-quant.

Maps Polygon EOD bars to namespace='bar' and corporate actions to
namespace='corporate_action'. Each emitted record carries the bitemporal
fields required by the PIT store: vt, kt, instrument_id, payload, source,
ingest_receipt, revision, superseded_by.

The adapter never reads the real POLYGON_API_KEY. HTTP is delegated to an
injectable ``transport`` callable so tests can supply canned responses.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Iterable

if TYPE_CHECKING:
    import requests

POLYGON_BASE = "https://api.polygon.io"


def _default_transport(url: str, params: dict, api_key: str) -> dict:
    """Real HTTP transport. Not used in tests; provided for completeness."""
    import requests

    resp = requests.get(
        url,
        params={**params, "apiKey": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def snapshot_pin(records: Iterable[dict]) -> str:
    """Stable SHA-256 manifest hash over an ordered iterable of records.

    Records are serialized canonically (sorted keys, compact separators) and
    concatenated with a length prefix so heterogeneous record sets pin
    unambiguously.
    """
    h = hashlib.sha256()
    for rec in records:
        blob = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
        h.update(len(blob).to_bytes(8, "big"))
        h.update(blob.encode("utf-8"))
    return h.hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _to_utc_ms(epoch_ms: int) -> datetime:
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc)


def _parse_date(value: int | str) -> datetime:
    """Parse a Polygon date field that may be epoch-millis or an ISO date string."""
    if isinstance(value, (int, float)):
        return _to_utc_ms(int(value))
    if isinstance(value, str):
        if value.isdigit():
            return _to_utc_ms(int(value))
        # ISO date, e.g. "2024-01-02" or "2024-01-02T00:00:00Z"
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    raise ValueError(f"unsupported date value: {value!r}")


@dataclass
class PolygonAdapter:
    """Adapter for Polygon.io EOD bars and corporate actions.

    Parameters
    ----------
    api_key:
        Polygon API key. Required by the real transport; tests inject a stub.
    transport:
        ``(url, params, api_key) -> dict`` callable. Defaults to
        ``_default_transport`` which uses ``requests``.
    revision:
        Monotonic revision label stamped on every record produced by this
        adapter instance. Bump it to mark a new ingest run.
    source:
        Provenance string stored on each record.
    """

    api_key: str
    transport: Callable[[str, str, dict], dict] = field(default=None)
    revision: int = 1
    source: str = "polygon"

    def __post_init__(self) -> None:
        if self.transport is None:
            self.transport = _default_transport

    def _receipt(self, endpoint: str, params: dict) -> dict:
        return {
            "endpoint": endpoint,
            "params": {k: v for k, v in params.items() if k != "apiKey"},
            "fetched_at": _iso(_utcnow()),
        }

    def fetch_bars(self, symbol: str, start: str, end: str) -> list[dict]:
        url = f"{POLYGON_BASE}/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
        params: dict[str, Any] = {"adjusted": "true", "limit": 50000}
        data = self.transport(url, params, self.api_key)
        return self._map_bars(symbol, data, params)

    def fetch_corporate_actions(self, symbol: str, start: str, end: str) -> list[dict]:
        url = f"{POLYGON_BASE}/v3/reference/dividends"
        params: dict[str, Any] = {"ticker": symbol, "limit": 1000}
        data = self.transport(url, params, self.api_key)
        dividends = self._map_dividends(symbol, data, params)
        url = f"{POLYGON_BASE}/v3/reference/splits"
        splits_data = self.transport(url, params, self.api_key)
        splits = self._map_splits(symbol, splits_data, params)
        return dividends + splits

    def _map_bars(self, symbol: str, data: dict, params: dict) -> list[dict]:
        receipt = self._receipt("/v2/aggs/ticker/range", params)
        kt = _iso(_utcnow())
        out: list[dict] = []
        for row in data.get("results", []):
            vt_dt = _to_utc_ms(int(row["t"]))
            out.append({
                "namespace": "bar",
                "vt": _iso(vt_dt),
                "kt": kt,
                "instrument_id": symbol,
                "payload": {
                    "open": row.get("o"),
                    "high": row.get("h"),
                    "low": row.get("l"),
                    "close": row.get("c"),
                    "volume": row.get("v"),
                    "vwap": row.get("vw"),
                    "trades": row.get("n"),
                },
                "source": self.source,
                "ingest_receipt": receipt,
                "revision": self.revision,
                "superseded_by": None,
            })
        return out

    def _map_dividends(self, symbol: str, data: dict, params: dict) -> list[dict]:
        receipt = self._receipt("/v3/reference/dividends", params)
        kt = _iso(_utcnow())
        out: list[dict] = []
        for row in data.get("results", []):
            vt_dt = _parse_date(row["ex_dividend_date"])
            out.append({
                "namespace": "corporate_action",
                "vt": _iso(vt_dt),
                "kt": kt,
                "instrument_id": symbol,
                "payload": {
                    "kind": "dividend",
                    "amount": row.get("cash_amount"),
                    "currency": row.get("currency"),
                    "declaration_date": row.get("declaration_date"),
                    "record_date": row.get("record_date"),
                    "pay_date": row.get("pay_date"),
                    "frequency": row.get("frequency"),
                },
                "source": self.source,
                "ingest_receipt": receipt,
                "revision": self.revision,
                "superseded_by": None,
            })
        return out

    def _map_splits(self, symbol: str, data: dict, params: dict) -> list[dict]:
        receipt = self._receipt("/v3/reference/splits", params)
        kt = _iso(_utcnow())
        out: list[dict] = []
        for row in data.get("results", []):
            vt_dt = _parse_date(row["execution_date"])
            out.append({
                "namespace": "corporate_action",
                "vt": _iso(vt_dt),
                "kt": kt,
                "instrument_id": symbol,
                "payload": {
                    "kind": "split",
                    "split_from": row.get("split_from"),
                    "split_to": row.get("split_to"),
                },
                "source": self.source,
                "ingest_receipt": receipt,
                "revision": self.revision,
                "superseded_by": None,
            })
        return out


__all__ = [
    "PolygonAdapter",
    "snapshot_pin",
    "POLYGON_BASE",
]
