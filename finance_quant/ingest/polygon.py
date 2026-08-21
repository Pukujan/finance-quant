"""Polygon.io market data adapter for finance-quant.

Maps Polygon EOD bars to namespace='bar' and corporate actions to
namespace='corporate_action'. Each emitted record carries the bitemporal
fields required by the PIT store: vt, kt, instrument_id, payload, source,
ingest_receipt, revision, superseded_by.

The adapter never reads the real POLYGON_API_KEY. HTTP is delegated to an
injectable ``transport`` callable so tests can supply canned responses.

Pagination
----------
Polygon paginates large result sets via:

- ``/v3/reference/*`` endpoints return a ``next_url`` field on the response
  body; the next page is fetched by issuing that URL as-is (the same
  transport callable receives it).
- ``/v2/aggs/*`` historically uses an opaque ``next_url`` as well; if
  absent, the adapter treats the response as the last page.

The :meth:`PolygonAdapter.fetch_bars` and
:meth:`PolygonAdapter.fetch_corporate_actions` methods walk all pages
transparently and emit one record per row across pages.

Rate limiting
-------------
A configurable :class:`finance_quant.ingest.polygon_config.RateLimitSettings`
instance governs the steady-state request rate and 429 retry/backoff
behavior. The helper :meth:`PolygonAdapter._throttle` sleeps just enough to
stay at or below the configured rate, and :meth:`_backoff_seconds` returns
the wait time for a given retry attempt (exponential, base configurable).
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping

if TYPE_CHECKING:
    import requests

from .polygon_config import DEFAULT_BASE_URL, PolygonConfig, RateLimitSettings

POLYGON_BASE = DEFAULT_BASE_URL


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


def _backoff_seconds(attempt: int, settings: RateLimitSettings) -> float:
    """Exponential backoff for retry attempt ``attempt`` (1-indexed).

    Returns ``backoff_base_seconds * 2 ** (attempt - 1)``. A real
    adapter would also respect ``Retry-After`` from the 429 response; this
    stub is a deterministic helper that does not.
    """
    if attempt < 1:
        return 0.0
    return settings.backoff_base_seconds * (2 ** (attempt - 1))


def _coerce_transport(
    transport: Callable[[str, dict, str], Any] | None,
    base_url: str,
    timeout: float,
) -> Callable[[str, dict, str], dict]:
    """Return a transport callable. ``None`` → real HTTP via ``requests``."""
    if transport is not None:
        return transport

    def _real(url: str, params: dict, api_key: str) -> dict:
        import requests

        resp = requests.get(
            url,
            params={**params, "apiKey": api_key},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    return _real


@dataclass
class PolygonAdapter:
    """Adapter for Polygon.io EOD bars and corporate actions.

    Parameters
    ----------
    api_key:
        Polygon API key. Required by the real transport; tests inject a stub.
    transport:
        ``(url, params, api_key) -> dict`` callable. Defaults to a
        ``requests``-based transport using ``base_url`` and ``timeout_seconds``.
    revision:
        Monotonic revision label stamped on every record produced by this
        adapter instance. Bump it to mark a new ingest run.
    source:
        Provenance string stored on each record.
    config:
        Optional :class:`PolygonConfig` instance. When provided, the other
        parameters (except ``transport``) are read from it. The dataclass
        fields ``base_url``, ``timeout_seconds``, ``rate_limit``, and
        ``extra`` are honored. ``api_key``, ``revision``, and ``source``
        on the adapter take precedence over the config when both are set.
    """

    api_key: str
    transport: Callable[[str, dict, str], Any] = field(default=None)
    revision: int = 1
    source: str = "polygon"
    config: PolygonConfig | None = None

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = PolygonConfig(
                api_key=self.api_key,
                source=self.source,
                revision=self.revision,
            )
        else:
            if not self.api_key:
                self.api_key = self.config.api_key
            # When a config is supplied, let it own source/revision so the
            # user has a single place to set them. The dataclass defaults
            # (revision=1, source="polygon") match PolygonConfig's defaults
            # so this is a no-op for callers who constructed the config
            # via PolygonConfig() with no overrides.
            self.source = self.config.source
            self.revision = self.config.revision
        self.transport = _coerce_transport(
            self.transport,
            self.config.base_url,
            self.config.timeout_seconds,
        )

    def _throttle(self) -> None:
        """Sleep enough to stay at or below the configured request rate.

        The free-tier default is 5 req/s, so a 0.2 s gap is sufficient.
        With ``sleep_enabled=False`` (e.g. in tests) this is a no-op.
        """
        settings = self.config.rate_limit
        if not settings.sleep_enabled:
            return
        delay = 1.0 / settings.requests_per_second
        time.sleep(delay)

    def _backoff(self, attempt: int) -> float:
        """Return the backoff wait in seconds for the given retry attempt.

        Stub: does not actually sleep here; the retry loop is the caller's
        responsibility. Real callers would do ``time.sleep(self._backoff(n))``
        between attempts.
        """
        return _backoff_seconds(attempt, self.config.rate_limit)

    def _receipt(self, endpoint: str, params: dict) -> dict:
        return {
            "endpoint": endpoint,
            "params": {k: v for k, v in params.items() if k != "apiKey"},
            "fetched_at": _iso(_utcnow()),
        }

    def _request_page(self, url: str, params: dict) -> dict:
        """Fetch one page, retrying rate limits with exponential backoff.

        Injected transports may return a response-like object (with
        ``status_code`` and ``json``), ``(status_code, payload)``, or a plain
        response mapping.  Supporting all three keeps HTTP behavior testable
        without changing the adapter's record contract.
        """
        settings = self.config.rate_limit
        for attempt in range(settings.max_retries + 1):
            response = self.transport(url, dict(params), self.api_key)
            status_code, data = self._decode_response(response)
            if status_code in (401, 403):
                raise RuntimeError(
                    f"Polygon authentication failed (HTTP {status_code}); "
                    "check POLYGON_API_KEY and its permissions"
                )
            if status_code == 429:
                if attempt >= settings.max_retries:
                    raise RuntimeError(
                        "Polygon rate limit exceeded (HTTP 429) after "
                        f"{settings.max_retries} retries"
                    )
                if settings.sleep_enabled:
                    time.sleep(self._backoff(attempt + 1))
                continue
            if status_code is not None and status_code >= 400:
                raise RuntimeError(f"Polygon request failed (HTTP {status_code})")
            if not isinstance(data, Mapping):
                raise ValueError("Malformed Polygon response: expected a JSON object")
            if "results" not in data:
                raise ValueError("Malformed Polygon response: missing 'results' field")
            if not isinstance(data["results"], list):
                raise ValueError("Malformed Polygon response: 'results' must be a list")
            return dict(data)
        raise RuntimeError("Polygon request failed unexpectedly")

    @staticmethod
    def _decode_response(response: Any) -> tuple[int | None, Any]:
        """Extract an optional HTTP status and JSON body from a transport result."""
        if isinstance(response, tuple) and len(response) == 2:
            return int(response[0]), response[1]
        if isinstance(response, Mapping):
            status_code = response.get("status_code")
            if status_code is not None:
                body = response.get("json", response.get("body", response))
                return int(status_code), body
            return None, response
        status_code = getattr(response, "status_code", None)
        json_method = getattr(response, "json", None)
        if callable(json_method):
            try:
                body = json_method()
            except Exception as exc:
                raise ValueError("Malformed Polygon response: invalid JSON") from exc
            return (int(status_code) if status_code is not None else None), body
        return None, response

    def _fetch_all_pages(
        self,
        url: str,
        params: dict,
        endpoint_label: str,
    ) -> tuple[list[dict], list[dict]]:
        """Walk all pages of a Polygon response.

        Returns ``(all_rows, per_page_data)``. Pagination follows
        ``response["next_url"]``; for ``/v2/aggs/`` the same convention is
        used (Polygon returns ``next_url`` when more pages are available).
        When no ``next_url`` is present, the first page is the last page.

        The per-page list is exposed so callers can attach a distinct
        ingest receipt per page if desired; for the current schema we use
        a single receipt per logical fetch in :meth:`_receipt`.
        """
        all_rows: list[dict] = []
        pages: list[dict] = []
        next_url: str | None = url
        next_params: dict | None = params
        while next_url:
            self._throttle()
            data = self._request_page(next_url, next_params or {})
            pages.append(data)
            all_rows.extend(data["results"])
            next_url = data.get("next_url") or None
            if next_url:
                # next_url is a fully-qualified URL; the next call should
                # not re-send the original params.
                next_params = {}
        return all_rows, pages

    def fetch_bars(self, symbol: str, start: str, end: str) -> list[dict]:
        url = (
            f"{self.config.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
        )
        params: dict[str, Any] = {"adjusted": "true", "limit": 50000}
        rows, _pages = self._fetch_all_pages(url, params, "/v2/aggs/ticker/range")
        return self._map_bars(symbol, {"results": rows}, params)

    def fetch_bars_mvfi(
        self, symbols: Iterable[str], start: str, end: str
    ) -> list[dict]:
        """Fetch daily bars for the small minimum-viable first-ingest batch."""
        records: list[dict] = []
        for symbol in symbols:
            records.extend(self.fetch_bars(symbol, start, end))
        return records

    def fetch_corporate_actions(self, symbol: str, start: str, end: str) -> list[dict]:
        # Note: Polygon v3 dividends/splits endpoints accept the date range
        # via query params; we pass them through for completeness.
        base_params: dict[str, Any] = {
            "ticker": symbol,
            "limit": 1000,
            "start_date": start,
            "end_date": end,
        }
        div_url = f"{self.config.base_url}/v3/reference/dividends"
        div_rows, _ = self._fetch_all_pages(div_url, base_params, "/v3/reference/dividends")
        dividends = self._map_dividends(symbol, {"results": div_rows}, base_params)

        split_url = f"{self.config.base_url}/v3/reference/splits"
        split_rows, _ = self._fetch_all_pages(split_url, base_params, "/v3/reference/splits")
        splits = self._map_splits(symbol, {"results": split_rows}, base_params)
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
    "_backoff_seconds",
]
