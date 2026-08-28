"""Replay the local workstation through historical daily paper sessions.

This is public research only. It reuses the workstation's strict walk-forward
predictions and the existing VirtualAccountStore; it never contacts a broker
and never enables live or paper-broker authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_quant.trader.account import VirtualAccountStore
from finance_quant.workstation.data import DailyBar, KgFact, fetch_daily_bars, fetch_sec_facts
from finance_quant.workstation.model import run


def _sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _atomic_json_write(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _validate_inputs(bars: Sequence[DailyBar], facts: Sequence[KgFact], *, ticker: str) -> None:
    if len(bars) < 80 or not facts:
        raise ValueError(f"input snapshot is too small for {ticker}")
    days = [bar.day for bar in bars]
    if days != sorted(set(days)):
        raise ValueError(f"input bars must be unique and chronological for {ticker}")
    for bar in bars:
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError(f"input bars must be finite for {ticker}")
        if min(bar.open, bar.high, bar.low, bar.close) <= 0 or bar.volume < 0:
            raise ValueError(f"input bars must be positive for {ticker}")


def _load_or_fetch_inputs(
    ticker: str,
    start: str,
    end: str,
    *,
    snapshot_dir: Path,
) -> tuple[list[DailyBar], list[KgFact], Path]:
    snapshot_path = snapshot_dir / f"{ticker.lower()}.json"
    if snapshot_path.exists():
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"invalid input snapshot: {snapshot_path}")
        if str(payload.get("ticker", "")).upper() != ticker.upper():
            raise ValueError(f"input snapshot ticker mismatch: {snapshot_path}")
        if str(payload.get("requested_start")) != start or str(payload.get("requested_end")) != end:
            raise ValueError(f"input snapshot date range mismatch: {snapshot_path}")
        bars = [DailyBar(**row) for row in payload.get("bars", [])]
        facts = [KgFact(**row) for row in payload.get("facts", [])]
        _validate_inputs(bars, facts, ticker=ticker)
        return bars, facts, snapshot_path

    bars = fetch_daily_bars(ticker, start, end)
    facts = fetch_sec_facts(ticker)
    _validate_inputs(bars, facts, ticker=ticker)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "workstation-paper-replay-input-v1",
        "ticker": ticker,
        "requested_start": start,
        "requested_end": end,
        "bars": [asdict(bar) for bar in bars],
        "facts": [asdict(fact) for fact in facts],
        "sources": {"price": "Yahoo chart endpoint", "fundamentals": "SEC CompanyFacts"},
    }
    snapshot_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return bars, facts, snapshot_path


def _quantity(state: Mapping[str, Any], ticker: str) -> int:
    for row in state.get("positions", []):
        if row.get("instrument_id") == ticker:
            return int(float(row.get("quantity", 0)))
    return 0


def _max_drawdown(values: Sequence[float]) -> float:
    peak = 0.0
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak:
            worst = min(worst, value / peak - 1.0)
    return worst


def replay(
    ticker: str,
    bars: Sequence[DailyBar],
    predictions: Sequence[Mapping[str, Any]],
    *,
    state_path: Path,
    initial_cash: float,
    allocation: float,
    slippage_bps: float,
) -> dict[str, Any]:
    if not bars or not predictions:
        raise ValueError("paper replay needs bars and walk-forward predictions")
    if not 0.0 <= allocation <= 1.0:
        raise ValueError("allocation must be between 0 and 1")
    if slippage_bps < 0 or not math.isfinite(slippage_bps):
        raise ValueError("slippage-bps must be finite and nonnegative")

    ordered_predictions = sorted(
        predictions,
        key=lambda row: (str(row["decision_day"]), str(row["outcome_day"])),
    )
    prediction_keys = [
        f"{index}:{row['decision_day']}:{row['outcome_day']}"
        for index, row in enumerate(ordered_predictions)
    ]
    if len(prediction_keys) != len(set(prediction_keys)):
        raise ValueError("replay predictions must have unique decision/outcome rows")
    by_day = {bar.day: bar for bar in bars}
    checkpoint_path = state_path.with_name(state_path.name + ".checkpoint.json")
    fingerprint = _canonical_sha256({
        "schema": "workstation-paper-replay-v2",
        "ticker": ticker,
        "bars": [asdict(bar) for bar in bars],
        "predictions": [dict(row) for row in ordered_predictions],
        "initial_cash": initial_cash,
        "allocation": allocation,
        "slippage_bps": slippage_bps,
    })
    state_exists = state_path.exists()
    checkpoint_exists = checkpoint_path.exists()
    if checkpoint_exists and not state_exists:
        raise ValueError(f"checkpoint exists without account state: {checkpoint_path}")
    account = VirtualAccountStore(
        state_path,
        initial_cash=initial_cash if not state_exists else None,
    )
    if state_exists and not checkpoint_exists:
        account.close()
        raise ValueError(f"existing account is missing replay checkpoint: {checkpoint_path}")
    if checkpoint_exists:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if not isinstance(checkpoint, Mapping) or checkpoint.get("fingerprint") != fingerprint:
            account.close()
            raise ValueError(f"replay checkpoint fingerprint mismatch: {checkpoint_path}")
        completed = set(str(key) for key in checkpoint.get("completed_keys", []))
        nav_values = [float(value) for value in checkpoint.get("nav_values", [initial_cash])]
        daily_return_sum = float(checkpoint.get("daily_return_sum", 0.0))
        daily_count = int(checkpoint.get("daily_count", 0))
        trade_notional = float(checkpoint.get("trade_notional", 0.0))
        long_sessions = int(checkpoint.get("long_sessions", 0))
    else:
        completed = set()
        nav_values = [float(initial_cash)]
        daily_return_sum = 0.0
        daily_count = 0
        trade_notional = 0.0
        long_sessions = 0
    try:
        for index, prediction in enumerate(ordered_predictions):
            prediction_key = prediction_keys[index]
            if prediction_key in completed:
                continue
            outcome_day = str(prediction["outcome_day"])
            bar = by_day.get(outcome_day)
            if bar is None or bar.open <= 0 or bar.close <= 0:
                raise ValueError(f"prediction has no valid execution bar: {outcome_day}")
            state = account.authoritative_state()
            current = _quantity(state, ticker)
            nav_open = float(account.nav({ticker: bar.open})["nav"])
            predicted = float(prediction["predicted"])
            target = math.floor(nav_open * allocation / bar.open) if predicted > 0 else 0
            if predicted > 0:
                long_sessions += 1
            delta = target - current
            if delta:
                side = "BUY" if delta > 0 else "SELL"
                quantity = abs(delta)
                slip = slippage_bps / 10_000.0
                fill_price = bar.open * (1.0 + slip if side == "BUY" else 1.0 - slip)
                seed = f"{ticker}:{prediction['decision_day']}:{outcome_day}:{side}:{quantity}"
                order_id = f"replay-order:{seed}"
                intent_id = f"replay-intent:{seed}"
                session_id = f"replay:{ticker}:{outcome_day}:{index}"
                event_time = f"{outcome_day}T13:30:00+00:00"
                with account.transaction():
                    account.submit_order(
                        order_id=order_id,
                        intent_id=intent_id,
                        session_id=session_id,
                        instrument_id=ticker,
                        side=side,
                        quantity=str(quantity),
                        created_at=event_time,
                    )
                    account.apply_fill(
                        fill_id=f"replay-fill:{seed}",
                        order_id=order_id,
                        session_id=session_id,
                        instrument_id=ticker,
                        quantity=str(quantity),
                        price=f"{fill_price:.8f}",
                        fee="0",
                        event_time=event_time,
                        source_event_id=f"replay-open:{ticker}:{outcome_day}",
                    )
                trade_notional += quantity * fill_price
            nav_close = float(account.nav({ticker: bar.close})["nav"])
            daily_return_sum += nav_close / nav_values[-1] - 1.0
            daily_count += 1
            nav_values.append(nav_close)
            completed.add(prediction_key)
            _atomic_json_write(checkpoint_path, {
                "schema": "workstation-paper-replay-checkpoint-v2",
                "fingerprint": fingerprint,
                "ticker": ticker,
                "completed_keys": sorted(completed),
                "nav_values": nav_values,
                "daily_return_sum": daily_return_sum,
                "daily_count": daily_count,
                "trade_notional": trade_notional,
                "long_sessions": long_sessions,
                "complete": len(completed) == len(ordered_predictions),
            })
        state = account.authoritative_state()
        final_nav = float(account.nav({ticker: bars[-1].close})["nav"])
        fills = len(state["fills"])
        orders = len(state["orders"])
        return {
            "ticker": ticker,
            "prediction_count": len(predictions),
            "long_sessions": long_sessions,
            "long_session_rate": long_sessions / len(predictions),
            "fills": fills,
            "orders": orders,
            "trade_notional": trade_notional,
            "initial_cash": initial_cash,
            "final_nav": final_nav,
            "marked_return": final_nav / initial_cash - 1.0,
            "max_drawdown": _max_drawdown(nav_values),
            "mean_daily_marked_return": daily_return_sum / daily_count if daily_count else 0.0,
            "state_hash": account.state_hash(),
            "account_path": str(state_path),
            "checkpoint_path": str(checkpoint_path),
        }
    finally:
        account.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", default="AAPL,MSFT,AMZN")
    parser.add_argument("--start", default="2018-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--snapshot-dir",
        help="directory containing frozen public bars/facts snapshots; defaults to <output-dir>/inputs",
    )
    parser.add_argument("--initial-cash", type=float, default=100_000.0)
    parser.add_argument("--allocation", type=float, default=0.95)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--min-train", type=int, default=126)
    parser.add_argument("--train-window", type=int, default=756)
    parser.add_argument("--retrain-every", type=int, default=21)
    args = parser.parse_args()
    tickers = tuple(dict.fromkeys(value.strip().upper() for value in args.tickers.split(",") if value.strip()))
    if not tickers:
        raise SystemExit("at least one ticker is required")
    if args.initial_cash <= 0 or not math.isfinite(args.initial_cash):
        raise SystemExit("initial-cash must be finite and positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else output_dir / "inputs"
    accounts_dir = output_dir / "accounts"
    accounts_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    source_manifest: list[dict[str, Any]] = []
    for ticker in tickers:
        bars, facts, snapshot_path = _load_or_fetch_inputs(
            ticker,
            args.start,
            args.end,
            snapshot_dir=snapshot_dir,
        )
        research = run(
            ticker,
            bars,
            facts,
            min_train=args.min_train,
            train_window=args.train_window,
            retrain_every=args.retrain_every,
        )
        for model_name in ("baseline", "kg"):
            replay_result = replay(
                ticker,
                bars,
                research["predictions"][model_name],
                state_path=accounts_dir / f"{ticker.lower()}-{model_name}.sqlite",
                initial_cash=args.initial_cash,
                allocation=args.allocation,
                slippage_bps=args.slippage_bps,
            )
            replay_result.update({
                "model": model_name,
                "model_metrics": research["metrics"][model_name],
                "data_start": research["start"],
                "data_end": research["end"],
                "bar_count": len(bars),
                "clock_semantics": "workstation daily bars; SEC facts visible by filed date; historical Yahoo bars are adjusted and do not provide source-native knowledge timestamps",
            })
            results.append(replay_result)
        source_manifest.append({
            "ticker": ticker,
            "start": args.start,
            "end": args.end,
            "bar_count": len(bars),
            "fact_count": len(facts),
            "input_snapshot": str(snapshot_path),
            "input_snapshot_sha256": _sha256_bytes(snapshot_path),
            "sources": {"price": "Yahoo chart endpoint", "fundamentals": "SEC CompanyFacts"},
        })

    manifest = {
        "analysis": {
            "name": "historical-workstation-paper-replay",
            "interpretation": "local zero-money historical simulation; not broker paper or live performance",
            "execution": "next-session open target rebalance, mark at next-session close",
            "allocation": args.allocation,
            "slippage_bps": args.slippage_bps,
            "model_training": "strict walk-forward ridge; baseline price features and kg price-plus-SEC-fact features",
        },
        "parameters": {
            "tickers": tickers,
            "start": args.start,
            "end": args.end,
            "initial_cash": args.initial_cash,
            "min_train": args.min_train,
            "train_window": args.train_window,
            "retrain_every": args.retrain_every,
            "snapshot_dir": str(snapshot_dir),
        },
        "sources": source_manifest,
        "results": results,
        "script_sha256": _sha256_bytes(Path(__file__).resolve()),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "results": results}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
