# Luna candidate implementation protocol

This file is the execution brief for a multi-agent implementation runner. The fixed laboratory in `finance_quant.lab` is already the benchmark/execution/scoring authority. Candidate agents build useful PIT data/state/KG/RAG/model/portfolio components against it; they do not redesign canonical outcome semantics locally.

## Start here

Read in order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. issue #35
4. issue #36
5. `docs/handoffs/LATEST.md`
6. issue #27 and the relevant implementation issue (#29, #37/#19, #21, #38, #32/#17, #39)
7. `finance_quant/lab/` and `tests/test_lab_*.py`

## First action: contract freeze, not another architecture rewrite

Before the broad worker fan-out, complete enough of #36 to freeze the walking-skeleton and shared contracts:

`SourceAdapter -> CanonicalObservation -> MarketState -> ForecastDistribution -> PortfolioIntent -> PaperFill -> CanonicalOutcome -> Score`

Freeze typed/serialized identities for the shared objects plus the machine-readable work-packet schema and tiered CI rules. This should be a short implementation step, not a new assurance program.

The fixed lab contracts below remain unchanged unless a concrete centrally coordinated integration bug requires it:

- `ComponentSpec` / content-addressed `ComponentRegistry`
- temporal observation schema `finance-quant.lab.temporal-observations.v1`
- `DecisionSnapshot` PIT freeze semantics
- exact `(lane, artifact_hash)` `ArmSpec` selection
- benchmark/candidate separation
- canonical `CanonicalOutcome` join after prediction
- `evaluation_hash` from actual snapshots/outcomes
- `ExperimentLedger` run identity
- router no-hindsight timing
- isolated `ShadowPaperLab`

## Initial bounded sphere

Do not attempt the whole world.

Initial research sphere:

- AI + semiconductors
- US + China + Taiwan
- roughly 50–100 equities/ETFs
- daily decisions initially
- 1d / 5d / 20d horizons

Interfaces remain asset-class-neutral, but crypto/prediction-market expansion is later work.

## Parallel worker lanes after #36 boundaries exist

### Market truth worker — #29

Build raw OHLCV plus separately timestamped splits/dividends/corporate actions. Do not use retrospectively adjusted history as authoritative raw PIT truth.

Required product tests: future corporate action cannot alter an earlier historical reconstruction; same source snapshot reconstructs deterministically; revision/version metadata remains inspectable.

### SEC/document worker — #29 / #37 / #19

Ingest filing text, filing timestamps, amendments and structured facts. Emit PIT observations/claims/evidence and provenance references.

Required tests: filing/amendment unavailable before publication; later amendment cannot rewrite an earlier state.

### Macro worker — #29 / #37

Implement historical-vintage macro observations, preferably ALFRED-style where available. Preserve release/revision times and publish versioned state inputs.

Required test: revised macro values cannot leak into earlier cuts.

### News/evidence worker — #29 / #37

Ingest historical financial news/events with publication/first-seen timestamps, entity resolution and syndicated-story dedup.

Do not equate mentions with independent evidence. Produce canonical story clusters plus `Observation`, `Claim`, `Evidence`, source lineage and attention/propagation measurements.

Required tests:

- future article cannot alter earlier cut;
- ingestion reordering with identical knowledge times cannot alter reconstructed state;
- duplicated syndication does not increase independent factual corroboration;
- extractor version creates a new immutable artifact rather than mutating old output.

### Trend/state worker — #37

Construct compact `TrendState` / `MarketState` components rather than forwarding raw documents to prediction models.

TrendState should include level, robust percentile/z-score, fast/medium/slow velocity, acceleration, noise, trend shape, change-point probability, novelty, persistence, saturation/decay and source diversity/cross-source confirmation.

Run direct ablations:

`price | +news/events | +TrendState | +MarketState`

Every executable arm enters historical WFO and forward local paper.

### Industrial/exposure graph worker — #37 / #19

Build temporal supplier/customer/competitor/product/industry/technology/geography exposure relations with provenance, confidence/materiality and historical knowledge times.

Traversal must remain bounded/typed: short default paths, explicit path grammars, top-K/beam limits, hub penalties/materiality decay and path/evidence dedup.

Required tests: path bounds obeyed; future relation evidence absent from earlier cuts; graph expansion cannot explode through hubs; same semantic relationship can coexist with separate empirical transmission measurements.

### PIT-safe retrieval / analog worker — #19

Implement two separate retrieval problems:

1. evidence retrieval: relevant current evidence after historical knowledge filtering;
2. historical analog retrieval: prior states/episodes whose outcomes were already resolved before the decision cut.

Required tests: future similar document/state cannot alter earlier retrieval; analog outcome must have resolved before `T`.

### Model workers — #21

Implement local predictive executors that consume only frozen inputs. Start with:

- linear/ridge/logistic baselines;
- historical-analog weighted-return predictor;
- LightGBM/XGBoost regression/ranking;
- selected temporal/neural models only when justified by data volume.

Prefer calibrated forecast distributions and cross-sectional ranking. No model executor owns canonical labels or reads unfrozen live data during prediction.

### Portfolio workers — #38

Take identical upstream forecast distributions/ranks and implement competing allocation policies:

1. equal-weight top-K;
2. edge/confidence-weighted top-K with position caps;
3. volatility-scaled/risk-budgeted allocation;
4. mean-variance/robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold policy.

Output immutable `PortfolioIntent`: target weights, buy/sell/hold deltas, cash target, expected return/risk/cost, turnover, binding constraints and provenance.

Diversification must account for theme/industry/geography/currency/factor/graph exposure rather than ticker count alone.

Each policy gets identical forecasts/cost assumptions and its own historical OOS comparison + persistent forward paper account.

## Candidate publication / evaluation flow

For each versioned component or policy:

1. implement against shared contracts;
2. add focused correctness tests plus property/metamorphic/mutation checks only where semantic risk warrants;
3. publish immutable component/model/policy identity;
4. assemble requested artifacts into the fixed benchmark;
5. declare explicit arms or a bounded matrix;
6. run with `finance-quant lab run --parallel N`;
7. start/continue its isolated zero-money forward paper account once executable;
8. report exact artifact hashes, arm IDs, evaluation hash, historical metrics and prospective paper state.

## Matrix strategy

Do not brute-force all combinations.

Stages:

1. price baseline;
2. one-lane main effects;
3. competing versions within useful lanes;
4. selected interactions;
5. MarketState / bounded KG / retrieval combinations;
6. model-family variants on the same information sets;
7. allocation-policy variants on the same forecasts;
8. contextual router/ensemble using prior resolved OOS only.

Use `max_arms` to fail accidental Cartesian explosions.

## Work-packet / handoff contract

Each worker must receive and return a durable work packet containing:

- issue/dependency IDs;
- exact owned files/modules;
- typed inputs/outputs;
- shared semantics it must preserve;
- forbidden authority;
- tests and product proof required;
- exact commits/artifact hashes/evaluation hashes;
- OOS results, including negative results;
- forward-paper account/state where applicable;
- operational metrics and known limitations.

Do not rely on chat history as the handoff authority.

## Verification policy

Use the cheapest validation layer that can credibly catch the failure:

- lint/strict typing/contracts for ordinary coding errors;
- TDD for concrete behavior;
- property/invariant tests for universal semantics;
- metamorphic tests for PIT/reordering/dedup/retrieval invariance;
- targeted mutation probes for one-character bugs that could create fake alpha or corrupt account truth;
- deterministic replay for run identity;
- Lean/SMT only for concrete hard invariants where executable tests are not enough;
- historical WFO and forward paper decide investment usefulness.

Correctness gates merges. Predictive metrics gate research promotion.

## Audit/export — #39

Do not block the first useful state/forecast/paper loops on RDF infrastructure. Once useful experiment lineages exist, export a Research Evidence Bundle using immutable manifests/ledger plus RDF/JSON-LD, OWL 2, SHACL, PROV-O, deterministic hashing and RO-Crate-style packaging where helpful.

## Safety/holdout

No broker/live capital work. Do not inspect private/sealed holdout contents without explicit authorization. Use development/public historical evaluation plus subsequent realized outcomes for normal iteration.
