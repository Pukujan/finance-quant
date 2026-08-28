"""Real price + SEC point-in-time knowledge inputs for the local workstation."""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

USER_AGENT = "finance-quant-local/0.1 contact=local-user"


class DataError(RuntimeError):
    pass


@dataclass(frozen=True)
class DailyBar:
    day: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class KgFact:
    concept: str
    value: float
    period_start: str | None
    period_end: str
    filed: str
    form: str
    accession: str


def _json(url: str, *, user_agent: str = USER_AGENT) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise DataError(f"failed to fetch {url}: {exc}") from exc


def _epoch(day: str) -> int:
    return int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp())


def fetch_daily_bars(ticker: str, start: str, end: str) -> list[DailyBar]:
    """Fetch adjusted daily OHLCV from Yahoo's public chart endpoint."""
    symbol = ticker.strip().upper()
    end_exclusive = (date.fromisoformat(end) + timedelta(days=1)).isoformat()
    query = urllib.parse.urlencode({
        "period1": _epoch(start), "period2": _epoch(end_exclusive),
        "interval": "1d", "events": "div,splits", "includeAdjustedClose": "true",
    })
    payload = _json(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}")
    chart = payload.get("chart", {}) if isinstance(payload, Mapping) else {}
    if chart.get("error"):
        raise DataError(str(chart["error"]))
    result = (chart.get("result") or [None])[0]
    if not isinstance(result, Mapping):
        raise DataError(f"no price data for {symbol}")
    ts = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quote = (indicators.get("quote") or [{}])[0]
    adj = (indicators.get("adjclose") or [{}])[0].get("adjclose") or []
    arrays = [quote.get(name) or [] for name in ("open", "high", "low", "close", "volume")]
    bars: list[DailyBar] = []
    for i, stamp in enumerate(ts):
        try:
            o, h, l, c, v = (arr[i] for arr in arrays)
        except (IndexError, TypeError):
            continue
        if any(x is None for x in (o, h, l, c)):
            continue
        raw_close = float(c)
        factor = 1.0
        if raw_close and i < len(adj) and adj[i] is not None:
            candidate = float(adj[i]) / raw_close
            if math.isfinite(candidate) and candidate > 0:
                factor = candidate
        day = datetime.fromtimestamp(int(stamp), tz=timezone.utc).date().isoformat()
        bars.append(DailyBar(day, float(o)*factor, float(h)*factor, float(l)*factor,
                             raw_close*factor, float(v or 0)/factor))
    bars.sort(key=lambda b: b.day)
    if len(bars) < 80:
        raise DataError(f"not enough bars for research: {len(bars)}")
    return bars


def fetch_sec_facts(ticker: str, *, user_agent: str = USER_AGENT) -> list[KgFact]:
    """Build a small real temporal KG from SEC companyfacts.

    Company -> reported concept is the edge; period_end is valid time and
    `filed` is knowledge time. Later amendments are later revisions.
    """
    mapping = _json("https://www.sec.gov/files/company_tickers.json", user_agent=user_agent)
    cik = None
    for item in mapping.values() if isinstance(mapping, Mapping) else ():
        if isinstance(item, Mapping) and str(item.get("ticker", "")).upper() == ticker.upper():
            cik = int(item["cik_str"]); break
    if cik is None:
        raise DataError(f"SEC has no CIK for {ticker}")
    payload = _json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", user_agent=user_agent)
    gaap = (((payload or {}).get("facts") or {}).get("us-gaap") or {})
    aliases = {
        "Revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"),
        "NetIncomeLoss": ("NetIncomeLoss", "ProfitLoss"),
        "Assets": ("Assets",),
        "Liabilities": ("Liabilities",),
    }
    out: list[KgFact] = []
    for canonical, candidates in aliases.items():
        concept = next((gaap[c] for c in candidates if isinstance(gaap.get(c), Mapping)), None)
        if not concept:
            continue
        units = concept.get("units") or {}
        rows = units.get("USD") or []
        for row in rows:
            if not isinstance(row, Mapping) or row.get("form") not in {"10-K", "10-Q", "10-K/A", "10-Q/A"}:
                continue
            if not row.get("filed") or not row.get("end") or row.get("val") is None:
                continue
            try:
                value = float(row["val"])
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                out.append(KgFact(canonical, value, str(row.get("start")) if row.get("start") else None,
                                  str(row["end"]), str(row["filed"]), str(row["form"]), str(row.get("accn", ""))))
    out.sort(key=lambda f: (f.filed, f.period_end, f.concept, f.accession))
    if not out:
        raise DataError(f"no usable SEC facts for {ticker}")
    return out


def visible_facts(facts: Sequence[KgFact], as_of: str) -> dict[str, list[KgFact]]:
    """Latest-known revision per concept/period at a historical knowledge cut."""
    latest: dict[tuple[str, str], KgFact] = {}
    for fact in facts:
        if fact.filed > as_of or fact.period_end > as_of:
            continue
        key = (fact.concept, fact.period_end)
        prior = latest.get(key)
        if prior is None or (fact.filed, fact.accession) > (prior.filed, prior.accession):
            latest[key] = fact
    grouped: dict[str, list[KgFact]] = {}
    for fact in latest.values():
        grouped.setdefault(fact.concept, []).append(fact)
    for rows in grouped.values():
        rows.sort(key=lambda f: (f.period_end, f.filed))
    return grouped


def _duration(f: KgFact) -> int | None:
    if not f.period_start:
        return None
    return (date.fromisoformat(f.period_end) - date.fromisoformat(f.period_start)).days


def _ratio(a: float, b: float) -> float:
    if not b:
        return 0.0
    return max(-10.0, min(10.0, a / abs(b)))


def kg_features(facts: Sequence[KgFact], as_of: str) -> tuple[float, float, float, float]:
    """PIT-safe [available, revenue growth, net margin, leverage]."""
    g = visible_facts(facts, as_of)
    rev, inc, assets, liab = (g.get(k, []) for k in ("Revenue", "NetIncomeLoss", "Assets", "Liabilities"))
    available = 1.0 if any((rev, inc, assets, liab)) else 0.0
    growth = margin = leverage = 0.0
    if len(rev) >= 2:
        latest, priors = rev[-1], rev[:-1]
        dur = _duration(latest)
        same = [p for p in priors if dur is not None and _duration(p) is not None and abs(_duration(p)-dur) <= 45]
        prior = (same or priors)[-1]
        growth = _ratio(latest.value-prior.value, prior.value)
    if rev and inc:
        r, dur = rev[-1], _duration(rev[-1])
        same = [x for x in inc if dur is not None and _duration(x) is not None and abs(_duration(x)-dur) <= 45]
        candidate = min(same or inc, key=lambda x: abs((date.fromisoformat(x.period_end)-date.fromisoformat(r.period_end)).days))
        margin = _ratio(candidate.value, r.value)
    if assets and liab:
        a = assets[-1]
        l = min(liab, key=lambda x: abs((date.fromisoformat(x.period_end)-date.fromisoformat(a.period_end)).days))
        leverage = _ratio(l.value, a.value)
    return available, growth, margin, leverage
