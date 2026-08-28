# Handoff — working predictive workstation MVP

Date: 2026-08-28
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #26
Product mode: local simulated paper only; no broker/live capital

## Direction

The active objective is no longer the old assurance ladder or an architecture bakeoff. Build, run and empirically improve the actual local quant product:

`real data -> PIT historical knowledge -> temporal KG/RAG/features -> local model -> walk-forward -> subsequent price outcome -> persistent local paper -> visible workstation`

Keep only correctness tests that catch genuine product bugs/leakage/account errors. Historical assurance artifacts remain in the repo but are not active product gates.

## Working implementation

`finance_quant/workstation/` now provides:

- real Yahoo adjusted daily prices;
- real SEC companyfacts converted into historical PIT facts;
- SEC filing-date knowledge cuts and report-period valid time;
- price-only and price+SEC-KG feature sets;
- local ridge training and strict walk-forward evaluation;
- separate current/latest signal generation;
- persistent SQLite paper account using `VirtualAccountStore`;
- next-session-open simulated fills;
- browser UI with price chart, predictions, KG facts, baseline comparison and paper account state.

Run:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

## First real-data result

Workflow run `33146074713` succeeded against real AAPL + SEC history through 2026-08-27. Focused workstation tests: **4 passed**.

Walk-forward count: **1,988**.

- price-only directional accuracy: **53.3702%**
- price+SEC-KG directional accuracy: **51.8612%**
- KG delta: **-1.5091 pp**
- price-only long/cash cumulative return: **+478.0179%**
- price+SEC-KG long/cash cumulative return: **+299.6102%**
- KG return delta: **-178.4077 pp**

Current conclusion: the first small SEC-fundamental KG **hurts this AAPL baseline**. Do not claim KG predictive value from infrastructure alone. Expand the information set/model and keep the same controlled ablation discipline.

## Paper result

Two consecutive real-data cutoffs reused one persistent local paper account:

- 2026-08-26 signal persisted;
- 2026-08-27 next-open execution occurred;
- fill: BUY 305 AAPL @ 310.61209779052734;
- marked NAV after the 2026-08-27 close: $101,210.2061 from $100,000 start.

No real capital or broker was involved.

## Correctness status

Focused product tests verify:

- filing-time PIT gating;
- no future-price contamination of earlier predictions;
- historical evaluation/live-signal separation;
- persistent account next-open fill and rerun idempotency.

A Windows full-suite execution recorded 1,039 passed / 25 skipped / 1 failed. The single failure is legacy bootstrap-document choreography (`#15` expected in the old handoff), not product code.

## Next exact action

Improve predictive quality and prove/disprove richer knowledge value:

1. expand temporal historical knowledge beyond four SEC concepts;
2. add PIT-safe filing text/RAG and entity/event/relationship edges;
3. run multi-symbol/cross-sectional walk-forward ablations;
4. introduce stronger local research/model tooling (Qlib/RD-Agent only where it accelerates this);
5. add continuous local paper refresh/signal/execution;
6. deepen the frontend so a decision point can show exactly what was known, predicted, traded and what price did afterward.

Do not return to assurance-phase sequencing unless a concrete product bug requires a specific old mechanism.
