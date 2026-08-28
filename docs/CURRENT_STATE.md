# Current project state

<!-- MACHINE-STATE: architecture=WORKING_LOCAL_QUANT_WORKSTATION_PLUS_LAB status=LUNA_CANDIDATE_EXECUTION_READY active_issue=27 -->

## Active direction

Build and empirically improve the working local quant workstation through a fixed parallel research laboratory:

`real historical data -> PIT normalization -> immutable versioned knowledge/model components -> assembled historical benchmark -> parallel walk-forward arms -> canonical realized market outcomes -> full-information scoring/router -> isolated persistent local paper accounts -> browser workstation`

The former assurance-phase ladder and OSS architecture bakeoff are not product gates. Historical evidence remains as implementation history. New research is judged by direct product correctness and unseen realized market outcomes.

Live capital is out of scope. Local simulated paper trading is enabled.

## Fixed laboratory/control plane is Luna-ready

`finance_quant.lab` is now the fixed measuring/execution layer for Luna or other candidate-generating agents. Candidate workers can publish many data/KG/RAG/model versions and run them in parallel without owning historical labels, PIT cuts, scoring, evaluation identity, or paper-account truth.

The autonomous flow is:

1. publish immutable component artifacts;
2. assemble PIT historical benchmark snapshots from registered component versions and fixed canonical outcomes;
3. declare explicit arms or a bounded arm matrix;
4. run all affordable arms concurrently;
5. score every arm against the same realized outcome at each decision point;
6. preserve exact component/evaluation/run lineage;
7. route using prior resolved OOS results only;
8. advance surviving arms in isolated zero-money shadow paper accounts.

### Public CLI

Publish a component:

`python -m finance_quant lab publish-component SPEC.json PAYLOAD.json --registry .lab-state/registry --output artifact.json`

Assemble a benchmark:

`python -m finance_quant lab assemble-benchmark EVALUATION.json COMPONENTS.json --registry .lab-state/registry --output benchmark.json`

Run candidate arms:

`python -m finance_quant lab run benchmark.json candidates.json --state-dir .lab-state --parallel 16 --output result.json`

`EVALUATION.json`/the assembled benchmark owns canonical outcomes. `CANDIDATES.json` owns only candidate arm/component/model/retrieval configuration. Candidate files are rejected if they contain snapshots, outcomes, labels, benchmark data, or experiment metadata.

## Stable lab contracts

### Versioned components

`ComponentSpec` + `ComponentRegistry` provide content-addressed immutable artifacts with:

- lane/name/version;
- code/input-dataset identity;
- schema/ontology/extractor/parameter identity;
- parent artifacts and dependency DAG;
- immutable payload bytes;
- descendant queries for selective downstream invalidation.

A standard temporal-observation artifact uses schema:

`finance-quant.lab.temporal-observations.v1`

with observations carrying `entity`, `known_at`, optional valid-time interval, and payload. Global observations may use entity `*`.

### Multiple versions at one historical cut

A frozen snapshot may contain several versions of the same semantic lane simultaneously, e.g.:

`price@v2 | news@v3 | news@v4 | KG-retriever@v5 | KG-retriever@v6`

Each `ArmSpec` selects exact `(lane, artifact_hash)` components. One arm still uses at most one artifact per semantic lane, but different arms can select different versions from the same frozen snapshot. This directly supports A/B/C/... version flywheels.

### Benchmark assembly

`assemble_benchmark` reads registered temporal artifacts and freezes each version at each fixed decision time **after PIT filtering**. Future-known rows are absent from the frozen snapshot. Canonical realized outcomes remain a separate evaluation input.

### Arm matrices

Candidate files may declare a bounded matrix with:

- fixed base components;
- named versions for variant lanes;
- explicit lane combinations/interactions;
- multiple model executors/configs;
- `max_arms` hard ceiling.

The lab expands this into exact immutable `ArmSpec`s. It never silently invents a full Cartesian product beyond the combinations requested.

### Full-information execution

Every affordable arm can predict every eligible historical decision. One canonical outcome is materialized per entity/decision/horizon and every arm is scored against that exact same outcome ID/cost assumptions.

The standard-library thread runner is the dependency-light baseline. Ray/Optuna/Qlib may be adapters later, not prerequisites for correctness.

### Experiment identity

`ExperimentLedger.RunSpec` now includes:

- knowledge manifest hash;
- retrieval policy hash;
- arm spec hash;
- router config hash;
- **evaluation hash**.

The evaluation hash is derived from actual frozen snapshot IDs and actual canonical outcome IDs, so changing historical input content or the realized answer necessarily creates a different experiment identity even if a human dataset label was left unchanged.

### Router and shadow paper

The first inspectable router is an exponentially weighted expert ensemble that only consumes outcomes resolved by the current historical decision time. Future unresolved arm performance cannot affect earlier weights.

`ShadowPaperLab` maintains one persistent authoritative `VirtualAccountStore` per arm. Accounts are isolated, restart-safe/idempotent, and zero-money simulation only.

## Correctness evidence

Dedicated workflow: `.github/workflows/lab-control-plane.yml`.

Latest green code run: **33173989475** at SHA `4ce8be50ecdc453d0ece0db440bf2b93f693063b`.

Results:

- lab correctness suite: **23 passed**;
- targeted semantic source mutations: **9/9 killed, 0 survived**;
- public benchmark/candidate CLI smoke: **passed**;
- existing workstation regression: **4/4 passed**;
- smoke artifact ID: **9686784711**;
- smoke artifact ZIP SHA256: `a0bdbcc9c2708c82dee482408387aff3a5248c7c2843022cb53f7a9bd5826354`.

The nine mutation probes deliberately corrupt:

1. future-known PIT filtering;
2. simultaneous same-lane version preservation;
3. direct snapshot future-time guard;
4. exact component selection;
5. canonical outcome coverage;
6. evaluation identity dependence on realized outcomes;
7. router no-hindsight timing;
8. candidate benchmark/label separation;
9. shadow-account restart behavior.

All nine are detected by the executable tests.

The smoke proves `price`, `price+news@v3`, and `price+news@v4` can run concurrently from the same frozen snapshot and receive the same canonical outcome ID. This is a synthetic control-plane proof, not predictive-performance evidence.

## Working workstation MVP retained

`finance_quant.workstation` remains runnable with:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

It still provides real Yahoo daily market history, SEC CompanyFacts PIT fundamentals, strict walk-forward ridge evaluation, persistent simulated paper execution, and browser inspection.

Real AAPL/SEC workflow `33146074713` produced 1,988 evaluated walk-forward predictions:

- price-only directional accuracy: **53.3702%**;
- price + current small SEC-fundamental feature set: **51.8612%**;
- delta: **-1.5091 percentage points**.

The current tiny SEC-fundamental set hurts this baseline. Do not claim KG predictive value from it. Historical simple long/cash metrics are also not a realistic cost-complete strategy result.

Existing zero-money paper proof remains:

- 2026-08-26 signal persisted;
- 2026-08-27 simulated next-open fill: **BUY 305 AAPL @ 310.61209779052734**;
- marked NAV: **$101,210.2061** from $100,000 starting cash.

That proves signal -> persistent state -> simulated execution -> marked account, not profitability.

## Active durable issues

- #12 master working local predictive quant workstation
- #26 workstation MVP + empirical iteration
- #27 versioned knowledge lanes + parallel full-information laboratory
- #28 component registry/manifests/DAG
- #29 historical PIT data lanes
- #30 parallel arm scheduler/shared outcomes
- #31 scoring/router/shadow paper
- #32 workstation experiment/lineage UI
- #19 temporal KG + PIT-safe RAG
- #21 local model research/training
- #18 continuous local paper refresh
- #17 browser workstation UX

## Next exact action

The shared executioner is ready. **Do not redesign its benchmark/outcome semantics inside candidate lanes.**

Luna should now spawn parallel workers against #29, #19 and #21 for:

1. raw OHLCV + timestamped corporate actions;
2. SEC filing text and amendments;
3. ALFRED-style macro vintages;
4. historical financial news/events with publication/first-known clocks and syndication dedup;
5. industrial supplier/customer/competitor relation extraction;
6. bounded temporal graph retrieval and PIT-safe RAG;
7. stronger local model families and cross-sectional models.

Each worker should emit immutable versioned temporal component artifacts and/or arm executors. The lab then assembles the fixed PIT benchmark and expands/runs explicit or matrix arms concurrently.

First substantive experiment family:

`price | +fundamentals | +news/hype | +events | +supply/competitors | +macro | +RAG | +bounded-KG | combined | contextual router`

across multiple symbols/regimes. Subsequent realized market prices remain the objective judge.

## Safety scope

- Local simulated paper: **ENABLED**.
- Parallel per-arm shadow paper: **ENABLED as simulation**.
- Broker-hosted paper: **not used**.
- Live capital: **DISABLED / out of scope**.
- Existing private/sealed holdout contents must not be inspected or optimized against without explicit authorization.

## Required read order for a fresh implementation session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/LATEST.md`
4. #27, then #28–#32
5. #29/#19/#21 for candidate work
6. `finance_quant/lab/`, `tests/test_lab_*.py`, `scripts/run_lab_mutation_probes.py`
7. `finance_quant/workstation/` and `tests/test_workstation_product.py`
8. older assurance material only when relevant to a concrete product bug
