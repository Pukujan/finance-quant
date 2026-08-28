"""Persistent zero-capital-risk local paper account advancement."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any


def _qty(state: dict, ticker: str) -> int:
    for p in state.get("positions",[]):
        if p.get("instrument_id")==ticker: return int(float(p.get("quantity",0)))
    return 0


def advance(research: dict[str,Any], *, state_dir: str|Path, initial_cash: float, allocation: float=.95, slippage_bps: float=2.0) -> dict[str,Any]:
    from finance_quant.trader.account import VirtualAccountStore
    ticker=research["ticker"]; root=Path(state_dir); root.mkdir(parents=True,exist_ok=True)
    db=root/f"{ticker.lower()}-paper.sqlite"; pending_file=root/f"{ticker.lower()}-pending.json"
    account=VirtualAccountStore(db,initial_cash=initial_cash if not db.exists() else None)
    try:
        pending=json.loads(pending_file.read_text()) if pending_file.exists() else None
        bars=research["bars"]; days=[b["day"] for b in bars]; by_day={b["day"]:b for b in bars}; executed=None
        if pending and pending["signal_day"] in by_day:
            i=days.index(pending["signal_day"])
            if i+1<len(days):
                b=by_day[days[i+1]]; state=account.authoritative_state(); current=_qty(state,ticker)
                nav=float(account.nav({ticker:b["open"]})["nav"]); target=math.floor(nav*allocation/b["open"]) if pending["predicted"]>0 else 0
                delta=target-current
                if delta:
                    side="BUY" if delta>0 else "SELL"; q=abs(delta); slip=slippage_bps/10000
                    price=b["open"]*(1+slip if side=="BUY" else 1-slip); seed=f"{ticker}:{pending['signal_day']}:{b['day']}:{side}:{q}"
                    account.submit_order(order_id=f"paper-order:{seed}",intent_id=f"paper-intent:{seed}",session_id=f"paper:{b['day']}",instrument_id=ticker,side=side,quantity=str(q),created_at=f"{b['day']}T13:30:00+00:00")
                    account.apply_fill(fill_id=f"paper-fill:{seed}",order_id=f"paper-order:{seed}",session_id=f"paper:{b['day']}",instrument_id=ticker,quantity=str(q),price=f"{price:.8f}",fee="0",event_time=f"{b['day']}T13:30:00+00:00",source_event_id=f"market-open:{ticker}:{b['day']}")
                    executed={"signal_day":pending["signal_day"],"fill_day":b["day"],"side":side,"quantity":q,"fill_price":price}
                pending=None
        live=research["live_signal"]
        if pending is None or pending.get("signal_day")!=live["day"]:
            pending={"ticker":ticker,"signal_day":live["day"],"predicted":live["kg_predicted"],"baseline_predicted":live["baseline_predicted"],"model":"price+pit-sec-kg-ridge"}
            pending_file.write_text(json.dumps(pending,indent=2,sort_keys=True),encoding="utf-8")
        state=account.authoritative_state(); mark=bars[-1]["close"]; nav=account.nav({ticker:mark})
        return {"account_path":str(db),"cash":float(nav["cash"]),"marked_position_value":float(nav["marked_position_value"]),"nav":float(nav["nav"]),"position_quantity":_qty(state,ticker),"orders":state.get("orders",[]),"fills":state.get("fills",[]),"pending_signal":pending,"executed_this_run":executed,"latest_mark":mark,"latest_day":bars[-1]["day"]}
    finally: account.close()
