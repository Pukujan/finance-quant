"""Configuration for the Polygon.io adapter.

Holds the API key, base URL, and rate-limit settings. The real key is loaded
from the ``POLYGON_API_KEY`` environment variable by :func:`load_from_env` —
the default ctor does **not** touch the environment, so tests can pass an
empty placeholder without leaking secrets.

The default rate-limit settings match Polygon's free tier documentation
(``https://polygon.io/docs/rest/options/options-rate-limiting`` as of 2024):
5 requests per second per API key, no burst.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


DEFAULT_BASE_URL = "https://api.polygon.io"


@dataclass
class RateLimitSettings:
    """Rate-limit knobs for the Polygon adapter.

    Parameters
    ----------
    requests_per_second:
        Steady-state cap. The rate-limit helper (see ``polygon.py``) sleeps
        enough between calls to stay at or below this rate. Default 5.
    burst:
        Maximum number of requests permitted in a single second before the
        backoff kicks in. Default 5 (i.e. no burst beyond the per-second cap).
    max_retries:
        Number of retry attempts on a 429 Too Many Requests response. Default 3.
    backoff_base_seconds:
        Initial backoff for the first retry. Subsequent retries use
        ``backoff_base_seconds * 2 ** (attempt - 1)`` (exponential). Default 1.0.
    sleep_enabled:
        When True the rate-limit helper actually sleeps. When False it is a
        no-op (useful for fast tests). Default True.
    """

    requests_per_second: float = 5.0
    burst: int = 5
    max_retries: int = 3
    backoff_base_seconds: float = 1.0
    sleep_enabled: bool = True

    def __post_init__(self) -> None:
        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if self.burst <= 0:
            raise ValueError("burst must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.backoff_base_seconds < 0:
            raise ValueError("backoff_base_seconds must be non-negative")


@dataclass
class PolygonConfig:
    """Configuration for the Polygon.io HTTP adapter.

    Parameters
    ----------
    api_key:
        Polygon API key. May be an empty string for tests; the real key is
        only required when the adapter actually issues HTTP requests.
    base_url:
        Scheme + host for the Polygon REST API. Override for sandbox / mock
        servers. Default ``https://api.polygon.io``.
    timeout_seconds:
        HTTP timeout for the default transport. Default 30.
    rate_limit:
        :class:`RateLimitSettings` instance. Default: free-tier settings.
    source:
        Provenance string stamped on every record. Default ``"polygon"``.
    revision:
        Initial revision label for the adapter. Default 1.
    extra:
        Free-form dict for downstream callers (e.g. ``{"plan": "free"}``).
    """

    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: float = 30.0
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    source: str = "polygon"
    revision: int = 1
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url must be a non-empty string")
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not isinstance(self.rate_limit, RateLimitSettings):
            self.rate_limit = RateLimitSettings(**self.rate_limit)

    @classmethod
    def load_from_env(
        cls,
        env: dict[str, str] | None = None,
        *,
        env_var: str = "POLYGON_API_KEY",
        default_api_key: str = "",
    ) -> "PolygonConfig":
        """Build a config from the environment.

        Reads the API key from ``env_var`` (default ``POLYGON_API_KEY``).
        The base URL and rate-limit settings use the dataclass defaults and
        may be overridden by other env vars (``POLYGON_BASE_URL``,
        ``POLYGON_RPS``, ``POLYGON_MAX_RETRIES``).

        The returned config is safe to construct even when the env var is
        unset; ``default_api_key`` is used in that case so callers can
        distinguish "no key" from "wrong key".
        """
        if env is None:
            env = os.environ
        api_key = env.get(env_var, default_api_key)
        cfg = cls(api_key=api_key)

        base = env.get("POLYGON_BASE_URL")
        if base:
            cfg.base_url = base

        rps = env.get("POLYGON_RPS")
        if rps:
            try:
                cfg.rate_limit.requests_per_second = float(rps)
            except ValueError as exc:
                raise ValueError(
                    f"POLYGON_RPS must be a float, got {rps!r}"
                ) from exc

        max_retries = env.get("POLYGON_MAX_RETRIES")
        if max_retries:
            try:
                cfg.rate_limit.max_retries = int(max_retries)
            except ValueError as exc:
                raise ValueError(
                    f"POLYGON_MAX_RETRIES must be an int, got {max_retries!r}"
                ) from exc

        return cfg


__all__ = [
    "DEFAULT_BASE_URL",
    "RateLimitSettings",
    "PolygonConfig",
]
