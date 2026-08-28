# Current project state

<!-- MACHINE-STATE: architecture=WORKING_LOCAL_QUANT_WORKSTATION status=PRODUCT_MVP_ACTIVE active_issue=26 -->

## Active direction

Build and empirically improve the working local quant workstation. The active product loop is:

`real prices + historical PIT information -> temporal KG/features -> local model -> strict walk-forward evaluation -> objective future-price outcome -> persistent local paper account -> browser UI`

The former assurance-phase ladder and OSS-architecture bakeoff are no longer product gates. Historical A1/A2 evidence remains in the repository as useful implementation history, but new work is driven by whether the local zero-capital product runs correctly and whether its predictive methods work out of sample.

Live-capital trading is still out of scope. Local simulated paper trading is the product target.

## Working workstation MVP

The durable branch contains `finance_quant.workstation`, runnable with:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

or:

`python -m finance_quant.workstation --ticker AAPL --start 2018-01-01 --capital 100000`

Current MVP capabilities:

- real adjusted daily OHLCV from Yahoo's chart endpoint;
- real SEC company-facts history for Revenue, NetIncomeLoss, Assets and Liabilities;
- historical knowledge gating by SEC `filed` date and report-period valid time;
- latest-known revision selection at each historical knowledge cut;
- price-only baseline features and price + PIT-SEC-KG features;
- local ridge-regression training with strict walk-forward temporal eligibility;
- objective next-session open-to-close return labels;
- baseline-vs-KG directional accuracy, correlation and long/cash return comparison;
- a separate latest-bar signal, distinct from labeled historical evaluation;
- persistent SQLite local paper account using the existing `VirtualAccountStore`;
- signal-at-close -> next-session-open simulated fills with configurable starting capital and slippage;
- browser UI showing price history, predictions, model comparison, latest PIT SEC facts, account NAV/cash/position and recent prediction outcomes.

## First real-data product run

GitHub Actions workflow `workstation-demo`, run `33146074713`, completed successfully on Ubuntu against real AAPL price history and real SEC company facts.

Window: 2018-01-01 through 2026-08-27.
Walk-forward evaluated predictions: **1,988**.

Results:

- price-only directional accuracy: **53.3702%**;
- price + SEC-KG directional accuracy: **51.8612%**;
- KG directional delta: **-1.5091 percentage points**;
- price-only long/cash cumulative return: **+478.0179%** over the evaluated daily signal sequence;
- price + SEC-KG long/cash cumulative return: **+299.6102%**;
- KG long/cash delta: **-178.4077 percentage points**;
- latest price-only prediction on 2026-08-27 input: **+0.2526%** next-session open-to-close;
- latest KG prediction: **+0.4105%**.

The current small SEC-fundamental KG therefore **does not improve the AAPL walk-forward baseline**. That is the first empirical result, not a failure of the workstation architecture. The next research task is to improve/expand the information graph and model and repeat controlled ablations across multiple symbols/regimes.

## Paper-trading proof

The same successful workflow ran two consecutive historical cutoffs using one persistent account state directory:

- 2026-08-26 close: form and persist a KG-model signal;
- 2026-08-27: execute that pending signal at the next session open;
- executed paper fill: **BUY 305 AAPL @ 310.61209779052734** including configured slippage;
- resulting marked paper NAV at the 2026-08-27 close: **$101,210.2061** from **$100,000** starting capital;
- position: **305 shares**.

This is local simulated paper only. It uses no broker and no real capital.

## Correctness checks kept

The focused workstation tests cover only product correctness properties that matter to the demo:

- SEC filing date is a historical knowledge gate;
- future prices cannot change earlier walk-forward predictions;
- historical labeled evaluation is distinct from the current live signal;
- persistent paper state fills the previous signal at the next open and does not duplicate the fill on rerun.

The focused suite passed 4/4 on the real-data demo runner. A separate Windows full-suite run reached **1,039 passed / 25 skipped / 1 failed**; the sole failure was an obsolete bootstrap-handoff assertion requiring `#15` in the old handoff, not a workstation failure.

## What is still missing

The MVP proves the complete loop but is intentionally small. The next product work is:

1. broaden the historical temporal KG beyond four SEC accounting concepts: filings/events, entities/relationships, industry/supply-chain/exposure edges and revisions;
2. add PIT-safe text/RAG evidence tied to each decision-time knowledge cut;
3. add stronger local model research/training and model comparison, likely adapting Qlib/RD-Agent where useful rather than blocking on them;
4. run multi-ticker and cross-sectional walk-forward experiments with benchmarks, costs and regime slices;
5. add a continuous/scheduled local paper runner that refreshes data, forms signals and advances the persistent account without manual reruns;
6. improve the browser workstation for model/KG ablations, trades/fills/PnL and click-through historical evidence;
7. keep replacing custom plumbing with OSS only when that materially accelerates the working product.

## Historical assets retained

Useful older assets remain available and may be reused where they help:

- bitemporal `vt/kt` PIT store and Polygon ingestion;
- Qlib compiler boundary;
- temporal graph design;
- pinned LEAN execution work;
- authoritative SQLite account/order/fill implementation;
- SessionReceipt/replay machinery;
- older assurance evidence and tests.

They are no longer mandatory phase gates for the local paper product.

## Safety scope

- Local simulated paper: **ENABLED as a product capability when the workstation is run**.
- Broker-hosted paper: **not used**.
- Live capital: **DISABLED / out of scope**.
- No hidden acceptance reruns are needed for product iteration.

## Next exact action

Improve the predictive engine, not the assurance shell. Start with a larger historical PIT knowledge dataset and controlled multi-symbol walk-forward ablation:

`price baseline vs price+fundamentals vs price+RAG vs price+temporal-KG vs combined`.

Keep the stock's subsequent realized price/return as the objective outcome and surface the comparison directly in the workstation.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/LATEST.md`
4. issue #12
5. issue #26
6. `finance_quant/workstation/` and `tests/test_workstation_product.py`
7. older architecture/assurance material only when relevant to a concrete implementation decision
