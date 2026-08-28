# Current project state

<!-- MACHINE-STATE: architecture=WORKING_LOCAL_QUANT_WORKSTATION_PLUS_LAB status=PRODUCT_FLYWHEEL_ACTIVE active_issue=27 -->

## Active direction

Build and empirically improve the working local quant workstation through a fixed parallel research laboratory. The active product loop is:

`real historical data -> PIT normalization -> versioned knowledge/model components -> parallel walk-forward arms -> canonical realized market outcomes -> full-information scoring/router -> isolated persistent local paper accounts -> browser workstation`

The former assurance-phase ladder and OSS-architecture bakeoff are no longer product gates. Historical A1/A2 evidence remains as implementation history. New work is judged by direct product correctness and unseen realized market outcomes.

Live-capital trading is out of scope. Local simulated paper trading is enabled.

## Fixed laboratory/control plane now implemented

`finance_quant.lab` is the fixed measuring machine intended for Luna/subagent candidate generation. Candidate code does not own historical labels, PIT cuts, scoring, run identity or paper-account truth.

Run the smoke interface with:

`python -m finance_quant lab run fixtures/lab/benchmark-smoke.json fixtures/lab/candidates-smoke.json --state-dir .lab-state --parallel 4`

The CLI deliberately separates:

- **benchmark file** — experiment metadata, frozen historical input candidates and canonical realized outcomes;
- **candidate file** — arm definitions/executor references/configuration only.

Candidate files are rejected if they contain snapshots, outcomes, labels or benchmark data.

Current control-plane capabilities:

- immutable `ComponentSpec` / `ComponentArtifact` identities;
- content-addressed local artifact registry with SQLite metadata and immutable payload files;
- exact `KnowledgeManifest` hashes for lane/component composition;
- dependency-DAG edges and descendant invalidation queries;
- PIT `TemporalLaneDatum` -> frozen `DecisionSnapshot` filtering before candidate execution;
- `ArmSpec` and `ExperimentBatchSpec` deterministic identities;
- arm executors receive only declared frozen lanes through `ArmContext`;
- arm knowledge-manifest hash must match the exact frozen artifact hashes it consumes;
- one canonical `CanonicalOutcome` per entity/decision/horizon, joined only after predictions are produced;
- sequential and parallel deterministic execution through the same runner;
- full-information scoring: every affordable arm at a decision point is scored against the same outcome ID/cost assumptions;
- ExperimentLedger run identity extended with knowledge/retrieval/arm/router hashes;
- first inspectable exponentially-weighted expert router using only outcomes resolved before decision time;
- persistent isolated `ShadowPaperLab` accounts backed by the existing authoritative `VirtualAccountStore`;
- restart/idempotency and per-arm account isolation semantics;
- dependency-light baseline uses standard-library thread parallelism; Ray/Optuna/Qlib can be adapters later rather than prerequisites.

## Laboratory correctness checks

Focused executable tests now cover the failure modes most likely to create convincing but invalid research:

- identical component spec/content -> identical artifact identity;
- new component versions do not mutate older artifacts;
- DAG descendant calculation does not invalidate siblings;
- manifest hashing is deterministic and one-artifact-per-lane;
- property-based future-known data insertion cannot change an earlier frozen snapshot;
- direct attempts to construct future-known snapshots are rejected;
- arms receive only declared lanes;
- claimed arm manifest must equal actual frozen lane artifact identities;
- deterministic sequential execution equals deterministic parallel execution;
- canonical outcome coverage is exact and every arm at a decision shares one outcome ID;
- router at T cannot learn from results whose outcomes resolve after T;
- ExperimentLedger identity is idempotent for identical arms and changes when the arm changes;
- candidate files cannot smuggle outcomes/labels into execution;
- shadow paper accounts are isolated across arms, survive restart and do not duplicate the same transition.

The dedicated workflow is `.github/workflows/lab-control-plane.yml`. It runs all `tests/test_lab_*.py`, executes the benchmark/candidate smoke end to end, runs the existing workstation regression tests, and uploads the smoke result.

## Working workstation MVP retained

`finance_quant.workstation` remains runnable with:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

Current workstation capabilities:

- real adjusted daily OHLCV from Yahoo's chart endpoint;
- real SEC company-facts history for Revenue, NetIncomeLoss, Assets and Liabilities;
- historical knowledge gating by SEC `filed` date and report-period valid time;
- latest-known revision selection at each historical knowledge cut;
- price-only baseline features and price + PIT-SEC-fundamental features;
- local ridge-regression training with strict walk-forward temporal eligibility;
- objective next-session open-to-close return labels;
- separate current/latest signal generation;
- persistent SQLite local paper account using `VirtualAccountStore`;
- next-session-open simulated fills;
- browser UI with price history, predictions, current PIT facts and paper-account state.

## First real-data product result retained

Workflow `workstation-demo` run `33146074713` succeeded against real AAPL + SEC history through 2026-08-27.

Walk-forward evaluated predictions: **1,988**.

- price-only directional accuracy: **53.3702%**;
- price + SEC-fundamental directional accuracy: **51.8612%**;
- knowledge delta: **-1.5091 percentage points**;
- price-only simple long/cash cumulative return: **+478.0179%**;
- price + SEC-fundamental simple long/cash cumulative return: **+299.6102%**.

The current small SEC-fundamental feature set hurts this AAPL baseline. Do not claim KG predictive value from infrastructure. The historical long/cash metric also does not yet represent a realistic cost-complete production strategy result.

## Existing paper proof retained

Two consecutive historical cutoffs reused one persistent local paper account:

- 2026-08-26 signal persisted;
- 2026-08-27 next-open execution occurred;
- fill: **BUY 305 AAPL @ 310.61209779052734** including configured slippage;
- marked NAV after the 2026-08-27 close: **$101,210.2061** from **$100,000** start.

This proves signal -> persistent state -> simulated execution -> marked account flow, not profitability.

## Active durable issues

- #12 master working local predictive quant workstation
- #26 working workstation MVP + empirical iteration
- #27 versioned knowledge lanes + parallel full-information experiment laboratory
- #28 component registry/manifests/DAG cache
- #29 historical PIT data lanes
- #30 parallel arm scheduler + shared outcomes/ExperimentLedger
- #31 scoring/router/shadow paper
- #32 workstation experiment/lineage UI
- #19 temporal KG + PIT-safe RAG lane
- #21 local model research/training lane
- #18 continuous local paper refresh
- #17 browser workstation UX

## What is still missing

The control plane now exists, but the high-value research lanes are still intentionally open for parallel implementation:

1. replace/augment retrospectively adjusted Yahoo history with raw OHLCV + separately timestamped corporate actions for strict PIT market truth;
2. ingest SEC filing text/amendments and publish immutable historical document artifacts;
3. add ALFRED-style macro vintages;
4. add historical financial news/event data with publication/first-known clocks and syndicated-story deduplication;
5. build historical industrial/supplier/customer/competitor relationships and bounded temporal graph retrieval;
6. add PIT-safe RAG document retrieval and provenance;
7. add stronger local model families and multi-symbol/cross-sectional experiments;
8. connect the lab results/shadow arms into workstation leaderboards and decision inspection;
9. add continuous forward refresh so surviving arms advance automatically in zero-money shadow paper.

These are suitable for Luna to implement with multiple subagents against the fixed lab contracts rather than redesigning the benchmark.

## Safety scope

- Local simulated paper: **ENABLED**.
- Parallel shadow paper per research arm: **ENABLED as local simulation**.
- Broker-hosted paper: **not used**.
- Live capital: **DISABLED / out of scope**.
- Old hidden acceptance/promotion choreography is not part of product iteration.

## Next exact action

Use the fixed laboratory as the executioner. Have Luna spawn independent workers for #29, #19 and #21 to publish real historical PIT data/knowledge/model candidates, then run their arms concurrently through the same benchmark/outcome/scoring path.

The first substantive experiment target remains:

`price vs price+fundamentals vs price+historical-news/hype vs price+events vs price+supply-chain/competitors vs price+macro vs price+RAG vs price+bounded-KG vs combined`

across multiple symbols/regimes, with subsequent realized market outcomes as the objective judge.

## Required read order for a fresh implementation session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/LATEST.md`
4. issue #27 and implementation issues #28–#32
5. #19 and #21 for candidate knowledge/model work
6. `finance_quant/lab/` and `tests/test_lab_*.py`
7. `finance_quant/workstation/` and `tests/test_workstation_product.py`
8. older architecture/assurance material only when relevant to a concrete product decision
