from __future__ import annotations
import math
from datetime import date,timedelta
from finance_quant.workstation.data import DailyBar,KgFact,kg_features,visible_facts
from finance_quant.workstation.model import examples,run,walk_forward
from finance_quant.workstation.paper import advance


def bars(n:int, shock:int|None=None):
    out=[]; p=100.0; d0=date(2018,1,1)
    for i in range(n):
        d=(d0+timedelta(days=i)).isoformat(); o=p*(1+.0007*math.sin(i/11)); intr=.0012*math.sin(i/17)+.0004
        if shock is not None and i>=shock: intr+=.08*math.sin(i)
        c=o*(1+intr); out.append(DailyBar(d,o,max(o,c)*1.002,min(o,c)*.998,c,1_000_000+i*500)); p=c
    return out


def facts():
    return [
        KgFact('Revenue',100,'2017-01-01','2017-12-31','2018-02-10','10-K','r1'),
        KgFact('NetIncomeLoss',10,'2017-01-01','2017-12-31','2018-02-10','10-K','n1'),
        KgFact('Assets',200,None,'2017-12-31','2018-02-10','10-K','a1'),
        KgFact('Liabilities',80,None,'2017-12-31','2018-02-10','10-K','l1'),
        KgFact('Revenue',120,'2018-01-01','2018-12-31','2019-02-10','10-K','r2'),
        KgFact('NetIncomeLoss',18,'2018-01-01','2018-12-31','2019-02-10','10-K','n2'),
        KgFact('Assets',220,None,'2018-12-31','2019-02-10','10-K','a2'),
        KgFact('Liabilities',85,None,'2018-12-31','2019-02-10','10-K','l2'),
    ]


def test_filing_date_is_historical_knowledge_gate():
    f=facts(); assert visible_facts(f,'2019-02-09')['Revenue'][-1].value==100
    assert visible_facts(f,'2019-02-10')['Revenue'][-1].value==120
    assert kg_features(f,'2019-02-09')[1]==0
    assert kg_features(f,'2019-02-10')[1]==.2


def test_future_prices_do_not_change_past_walk_forward_predictions():
    f=facts(); a=walk_forward(examples(bars(440),f,with_kg=True),min_train=80,train_window=180,retrain_every=13)
    b=walk_forward(examples(bars(520,shock=440),f,with_kg=True),min_train=80,train_window=180,retrain_every=13); lookup={x.decision_day:x for x in b}
    assert a
    for x in a:
        assert lookup[x.decision_day].predicted==x.predicted
        assert lookup[x.decision_day].actual==x.actual


def test_historical_evaluation_and_live_signal_are_separate():
    b=bars(420); r=run('TEST',b,facts(),min_train=80,train_window=180,retrain_every=13)
    assert r['predictions']['kg'][-1]['decision_day']==b[-2].day
    assert r['predictions']['kg'][-1]['outcome_day']==b[-1].day
    assert r['live_signal']['day']==b[-1].day
    assert math.isfinite(r['live_signal']['kg_predicted'])


def test_persistent_paper_fills_previous_signal_at_next_open(tmp_path):
    first_bars=[
        {'day':'2026-08-26','open':99.0,'high':102.0,'low':98.0,'close':101.0,'volume':1_000_000},
        {'day':'2026-08-27','open':101.0,'high':104.0,'low':100.0,'close':103.0,'volume':1_100_000},
    ]
    first={'ticker':'TEST','bars':first_bars,'live_signal':{'day':'2026-08-27','baseline_predicted':.01,'kg_predicted':.02}}
    a=advance(first,state_dir=tmp_path,initial_cash=1000,allocation=.9,slippage_bps=0)
    assert a['fills']==[]
    assert a['pending_signal']['signal_day']=='2026-08-27'
    second_bars=first_bars+[{'day':'2026-08-28','open':100.0,'high':106.0,'low':99.0,'close':105.0,'volume':1_200_000}]
    second={'ticker':'TEST','bars':second_bars,'live_signal':{'day':'2026-08-28','baseline_predicted':.005,'kg_predicted':.01}}
    b=advance(second,state_dir=tmp_path,initial_cash=999999,allocation=.9,slippage_bps=0)
    assert len(b['fills'])==1
    assert b['executed_this_run']['fill_day']=='2026-08-28'
    assert b['executed_this_run']['fill_price']==100.0
    assert b['position_quantity']==9
    c=advance(second,state_dir=tmp_path,initial_cash=1,allocation=.9,slippage_bps=0)
    assert len(c['fills'])==1
    assert c['position_quantity']==9
