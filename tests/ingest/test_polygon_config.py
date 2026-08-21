"""Tests for the PolygonConfig dataclass and PolygonConfig.load_from_env."""
from __future__ import annotations

import pytest

from finance_quant.ingest.polygon_config import (
    DEFAULT_BASE_URL,
    PolygonConfig,
    RateLimitSettings,
)


# -- PolygonConfig defaults ---------------------------------------------


def test_default_config_has_empty_api_key():
    cfg = PolygonConfig()
    assert cfg.api_key == ""
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.timeout_seconds == 30.0
    assert isinstance(cfg.rate_limit, RateLimitSettings)
    assert cfg.rate_limit.requests_per_second == 5.0
    assert cfg.revision == 1
    assert cfg.source == "polygon"
    assert cfg.extra == {}


def test_trailing_slash_stripped_from_base_url():
    cfg = PolygonConfig(base_url="https://example.com/")
    assert cfg.base_url == "https://example.com"


def test_invalid_timeout_raises():
    with pytest.raises(ValueError):
        PolygonConfig(timeout_seconds=0)
    with pytest.raises(ValueError):
        PolygonConfig(timeout_seconds=-1)


def test_empty_base_url_raises():
    with pytest.raises(ValueError):
        PolygonConfig(base_url="")


def test_extra_dict_is_independent_per_instance():
    a = PolygonConfig()
    b = PolygonConfig()
    a.extra["plan"] = "free"
    assert "plan" not in b.extra


def test_extra_dict_does_not_share_default():
    a = PolygonConfig()
    a.extra["x"] = 1
    b = PolygonConfig()
    assert "x" not in b.extra


# -- RateLimitSettings validation ---------------------------------------


def test_rate_limit_rejects_nonpositive_rps():
    with pytest.raises(ValueError):
        RateLimitSettings(requests_per_second=0)
    with pytest.raises(ValueError):
        RateLimitSettings(requests_per_second=-1)


def test_rate_limit_rejects_nonpositive_burst():
    with pytest.raises(ValueError):
        RateLimitSettings(burst=0)


def test_rate_limit_rejects_negative_max_retries():
    with pytest.raises(ValueError):
        RateLimitSettings(max_retries=-1)


def test_rate_limit_rejects_negative_backoff():
    with pytest.raises(ValueError):
        RateLimitSettings(backoff_base_seconds=-0.1)


# -- PolygonConfig.load_from_env ----------------------------------------


def test_load_from_env_picks_up_api_key():
    cfg = PolygonConfig.load_from_env({"POLYGON_API_KEY": "abc123"})
    assert cfg.api_key == "abc123"


def test_load_from_env_uses_default_when_key_missing():
    cfg = PolygonConfig.load_from_env({}, default_api_key="")
    assert cfg.api_key == ""


def test_load_from_env_overrides_base_url():
    cfg = PolygonConfig.load_from_env({
        "POLYGON_API_KEY": "x",
        "POLYGON_BASE_URL": "https://sandbox.example.com",
    })
    assert cfg.base_url == "https://sandbox.example.com"


def test_load_from_env_overrides_rps():
    cfg = PolygonConfig.load_from_env({
        "POLYGON_API_KEY": "x",
        "POLYGON_RPS": "12.5",
    })
    assert cfg.rate_limit.requests_per_second == 12.5


def test_load_from_env_overrides_max_retries():
    cfg = PolygonConfig.load_from_env({
        "POLYGON_API_KEY": "x",
        "POLYGON_MAX_RETRIES": "7",
    })
    assert cfg.rate_limit.max_retries == 7


def test_load_from_env_rejects_non_float_rps():
    with pytest.raises(ValueError):
        PolygonConfig.load_from_env({
            "POLYGON_API_KEY": "x",
            "POLYGON_RPS": "not-a-number",
        })


def test_load_from_env_rejects_non_int_max_retries():
    with pytest.raises(ValueError):
        PolygonConfig.load_from_env({
            "POLYGON_API_KEY": "x",
            "POLYGON_MAX_RETRIES": "many",
        })


def test_load_from_env_ignores_blank_optional_vars():
    cfg = PolygonConfig.load_from_env({
        "POLYGON_API_KEY": "x",
        "POLYGON_BASE_URL": "",
        "POLYGON_RPS": "",
        "POLYGON_MAX_RETRIES": "",
    })
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.rate_limit.requests_per_second == 5.0
    assert cfg.rate_limit.max_retries == 3


# -- Adapter wires config -----------------------------------------------


def test_adapter_uses_config_when_provided():
    cfg = PolygonConfig(
        api_key="from-cfg",
        base_url="https://cfg.example.com",
        source="cfg-source",
        revision=42,
    )
    from finance_quant.ingest.polygon import PolygonAdapter
    a = PolygonAdapter(api_key="", transport=lambda u, p, k: {"results": []}, config=cfg)
    assert a.api_key == "from-cfg"
    assert a.source == "cfg-source"
    assert a.revision == 42
    assert a.config.base_url == "https://cfg.example.com"


def test_adapter_api_key_arg_overrides_config():
    cfg = PolygonConfig(api_key="from-cfg")
    from finance_quant.ingest.polygon import PolygonAdapter
    a = PolygonAdapter(api_key="from-arg", transport=lambda u, p, k: {"results": []}, config=cfg)
    assert a.api_key == "from-arg"


def test_adapter_without_config_gets_synthesized_config():
    from finance_quant.ingest.polygon import PolygonAdapter
    a = PolygonAdapter(api_key="k", transport=lambda u, p, k: {"results": []})
    assert isinstance(a.config, PolygonConfig)
    assert a.config.api_key == "k"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
