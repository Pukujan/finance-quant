"""Small local predictive model and strict walk-forward evaluator."""
from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Sequence

from .data import DailyBar, KgFact, kg_features, visible_facts

PRICE_FEATURES = ("ret_1d", "ret_5d", "ret_20d", "momentum_60d", "volatility_20d", "volume_z_20d")
KG_FEATURES = ("kg_available", "revenue_growth", "net_margin", "leverage")


@dataclass(frozen=True)
class Example:
    decision_day: str; outcome_day: str; features: tuple[float, ...]; target: float


@dataclass(frozen=True)
class Prediction:
    decision_day: str; outcome_day: str; predicted: float; actual: float


@dataclass(frozen=True)
class Metrics:
    count: int; directional_accuracy: float; mae: float; rmse: float; correlation: float; long_cash_return: float


def _ret(closes: Sequence[float], i: int, n: int) -> float:
    return closes[i] / closes[i-n] - 1.0 if i >= n and closes[i-n] else 0.0


def price_features(bars: Sequence[DailyBar], i: int) -> tuple[float, ...]:
    if i < 60:
        raise ValueError("need 60 prior bars")
    c = [b.close for b in bars]; v = [b.volume for b in bars]
    returns = [c[j]/c[j-1]-1.0 for j in range(i-19, i+1) if c[j-1]]
    vw = v[i-19:i+1]; vm = statistics.fmean(vw); vs = statistics.pstdev(vw) or 1.0
    return (_ret(c,i,1), _ret(c,i,5), _ret(c,i,20), _ret(c,i,60), statistics.pstdev(returns), max(-10,min(10,(v[i]-vm)/vs)))


def examples(bars: Sequence[DailyBar], facts: Sequence[KgFact], *, with_kg: bool) -> list[Example]:
    out = []
    for i in range(60, len(bars)-1):
        nxt = bars[i+1]
        if nxt.open <= 0: continue
        f = price_features(bars, i) + (kg_features(facts, bars[i].day) if with_kg else ())
        out.append(Example(bars[i].day, nxt.day, f, nxt.close/nxt.open-1.0))
    return out


def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    n=len(b); aug=[row[:] + [b[i]] for i,row in enumerate(a)]
    for col in range(n):
        p=max(range(col,n), key=lambda r:abs(aug[r][col])); aug[col],aug[p]=aug[p],aug[col]
        if abs(aug[col][col]) < 1e-12: aug[col][col]=1e-12
        scale=aug[col][col]; aug[col]=[x/scale for x in aug[col]]
        for r in range(n):
            if r==col: continue
            k=aug[r][col]
            if k: aug[r]=[x-k*y for x,y in zip(aug[r],aug[col])]
    return [aug[i][-1] for i in range(n)]


@dataclass(frozen=True)
class Ridge:
    means: tuple[float,...]; scales: tuple[float,...]; beta: tuple[float,...]
    def predict(self, x: Sequence[float]) -> float:
        z=[(float(v)-m)/s for v,m,s in zip(x,self.means,self.scales)]
        return self.beta[0]+sum(b*v for b,v in zip(self.beta[1:],z))


def fit(rows: Sequence[Example], ridge: float=1e-3) -> Ridge:
    d=len(rows[0].features)
    means=[statistics.fmean(r.features[j] for r in rows) for j in range(d)]
    scales=[statistics.pstdev(r.features[j] for r in rows) or 1.0 for j in range(d)]
    x=[[1.0]+[(r.features[j]-means[j])/scales[j] for j in range(d)] for r in rows]; y=[r.target for r in rows]
    p=d+1; xtx=[[0.0]*p for _ in range(p)]; xty=[0.0]*p
    for row,target in zip(x,y):
        for i in range(p):
            xty[i]+=row[i]*target
            for j in range(p): xtx[i][j]+=row[i]*row[j]
    for i in range(1,p): xtx[i][i]+=ridge
    return Ridge(tuple(means),tuple(scales),tuple(_solve(xtx,xty)))


def walk_forward(rows: Sequence[Example], *, min_train: int=126, train_window: int=756, retrain_every: int=21) -> list[Prediction]:
    out=[]; model=None; last=-10**9
    for pos,row in enumerate(rows):
        eligible=[r for r in rows[:pos] if r.outcome_day <= row.decision_day]
        if len(eligible)<min_train: continue
        if model is None or pos-last>=retrain_every:
            model=fit(eligible[-train_window:]); last=pos
        out.append(Prediction(row.decision_day,row.outcome_day,model.predict(row.features),row.target))
    return out


def live_prediction(bars: Sequence[DailyBar], facts: Sequence[KgFact], *, with_kg: bool, min_train: int=126, train_window: int=756) -> float:
    rows=examples(bars,facts,with_kg=with_kg)
    eligible=[r for r in rows if r.outcome_day <= bars[-1].day]
    if len(eligible)<min_train: raise ValueError("not enough resolved labels")
    x=price_features(bars,len(bars)-1)+(kg_features(facts,bars[-1].day) if with_kg else ())
    return fit(eligible[-train_window:]).predict(x)


def metrics(preds: Sequence[Prediction]) -> Metrics:
    if not preds: return Metrics(0,0,0,0,0,0)
    err=[p.predicted-p.actual for p in preds]; px=[p.predicted for p in preds]; ay=[p.actual for p in preds]
    mx,my=statistics.fmean(px),statistics.fmean(ay); dx=[x-mx for x in px]; dy=[y-my for y in ay]
    den=math.sqrt(sum(x*x for x in dx)*sum(y*y for y in dy)); corr=0 if den==0 else sum(x*y for x,y in zip(dx,dy))/den
    cap=1.0
    for p in preds:
        if p.predicted>0: cap*=1+p.actual
    return Metrics(len(preds),statistics.fmean((p.predicted>=0)==(p.actual>=0) for p in preds),statistics.fmean(abs(x) for x in err),math.sqrt(statistics.fmean(x*x for x in err)),corr,cap-1)


def run(ticker: str, bars: Sequence[DailyBar], facts: Sequence[KgFact], *, min_train: int=126, train_window: int=756, retrain_every: int=21) -> dict:
    base=walk_forward(examples(bars,facts,with_kg=False),min_train=min_train,train_window=train_window,retrain_every=retrain_every)
    kg=walk_forward(examples(bars,facts,with_kg=True),min_train=min_train,train_window=train_window,retrain_every=retrain_every)
    bm,km=metrics(base),metrics(kg)
    visible=visible_facts(facts,bars[-1].day); latest=[rows[-1] for rows in visible.values() if rows]
    latest.sort(key=lambda f:(f.filed,f.period_end),reverse=True)
    return {
        "ticker":ticker.upper(),"start":bars[0].day,"end":bars[-1].day,"bars":[asdict(b) for b in bars],
        "features":{"baseline":list(PRICE_FEATURES),"kg":list(PRICE_FEATURES+KG_FEATURES)},
        "metrics":{"baseline":asdict(bm),"kg":asdict(km),"delta":{"directional_accuracy":km.directional_accuracy-bm.directional_accuracy,"correlation":km.correlation-bm.correlation,"long_cash_return":km.long_cash_return-bm.long_cash_return}},
        "predictions":{"baseline":[asdict(p) for p in base],"kg":[asdict(p) for p in kg]},
        "live_signal":{"day":bars[-1].day,"baseline_predicted":live_prediction(bars,facts,with_kg=False,min_train=min_train,train_window=train_window),"kg_predicted":live_prediction(bars,facts,with_kg=True,min_train=min_train,train_window=train_window)},
        "latest_kg_facts":[asdict(f) for f in latest[:16]],
        "sources":{"price":"Yahoo chart endpoint","kg":"SEC companyfacts (filed=date knowledge cut)"},
    }
