# Luna candidate implementation protocol

This file is the execution brief for a multi-agent implementation runner. The fixed laboratory in `finance_quant.lab` is already the benchmark/execution/scoring authority. Candidate agents build useful PIT data, signal, state, KG/RAG, model/meta and portfolio components against it; they do not redesign canonical outcome semantics locally.

## Start here

Read in order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`
4. issue #35
5. issue #36
6. `docs/handoffs/LATEST.md`
7. issue #27 and the relevant implementation issue (#29, #37/#19, #21, #38, #32/#17, #39)
8. `finance_quant/lab/` and `tests/test_lab_*.py`

## Latest product framing

The parent product is an **adaptive modular multi-strategy quantitative portfolio engine**:

`heterogeneous signal providers -> model/meta weights -> forecast distributions/ranks -> portfolio allocation -> local zero-money paper -> realized outcomes -> weight/version evolution`

Do not treat MarketState/KG/RAG/news as mandatory. They are candidate signal-provider families alongside price, momentum, breakout, volatility, fundamentals, macro, vendor quantified feeds and future strategies.

The engine must be able to discover that a sophisticated provider deserves zero active weight.

## First action: reconcile and freeze contracts, not another architecture rewrite

#35/#36 were written before the final strategy-centric clarification. Before the broad worker fan-out, reconcile them and freeze the smallest shared contracts so a simple technical strategy and a rich MarketState strategy both traverse the same engine.

Target permanent skeleton concept:

`PIT data/sources -> SignalProvider(s) -> immutable signal/forecast artifacts -> model/meta weights -> ForecastDistribution -> PortfolioIntent -> PaperFill -> CanonicalOutcome -> Score -> future weight/version update`

`MarketState` may be produced inside one provider but must not be the universal mandatory intermediate.

Freeze typed/serialized identities for the shared objects plus the machine-readable work-packet schema and tiered CI rules. Likely shared concepts include:

- `SignalProvider` / `SignalArtifact` or `SignalVector`;
- `ForecastDistribution`;
- `StrategySpec`;
- meta/router weight state;
- `PortfolioIntent`;
- paper execution/fill identity;
- `CanonicalOutcome`;
- immutable artifact/version identity.

This should be a short implementation step, not a new assurance program.

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

## Parallel worker lanes after #36 boundaries exist

### Market truth worker — #29

Build raw OHLCV plus separately timestamped splits/dividends/corporate actions. Do not use retrospectively adjusted history as authoritative raw PIT truth.

Required product tests: future corporate action cannot alter an earlier historical reconstruction; same source snapshot reconstructs deterministically; revision/version metadata remains inspectable.

### Technical signal worker — engine foundation

Implement first-class versioned price-derived providers that prove the engine does not depend on knowledge infrastructure. Candidate initial providers:

- momentum/trend;
- breakout;
- volatility/state;
- optionally simple mean-reversion/technical controls.

Emit the same shared signal/forecast contract used by richer providers. Required tests focus on deterministic feature timing, no future-bar leakage and exact provider/version identity.

Each executable technical strategy should enter historical WFO and local forward paper immediately.

### SEC/document worker — #29 / #37 / #19

Ingest filing text, filing timestamps, amendments and structured facts. Emit PIT observations/claims/evidence and provenance references that can feed fundamental and/or MarketState signal providers.

Required tests: filing/amendment unavailable before publication; later amendment cannot rewrite an earlier state.

### Macro worker — #29 / #37

Implement historical-vintage macro observations, preferably ALFRED-style where available. Preserve release/revision times and publish versioned macro signal/state inputs.

Required test: revised macro values cannot leak into earlier cuts.

### News / pre-quantized evidence worker — #29 / #37

Support both custom/open extraction and adapter-style pre-quantized sources where legally/technically available. Examples may include GDELT/open corpora and optional commercial RavenPack/LSEG/FactSet-style feeds.

Do not equate mentions with independent evidence. For custom evidence, produce canonical story clusters plus `Observation`, `Claim`, `Evidence`, source lineage and attention/propagation measurements.

Required tests:

- future article/score cannot alter earlier cut;
- ingestion reordering with identical knowledge times cannot alter reconstructed signal/state;
- duplicated syndication does not increase independent factual corroboration;
- provider/extractor version creates a new immutable artifact rather than mutating old output.

### Trend/state worker — #37

Construct compact `TrendState` / `MarketState` **signal-provider outputs**, not a mandatory product intermediate.

TrendState can include level, robust percentile/z-score, fast/medium/slow velocity, acceleration, noise, trend shape, change-point probability, novelty, persistence, saturation/decay and source diversity/cross-source confirmation.

Run provider variants through the same forecast/meta/portfolio engine as technical strategies.

### Industrial/exposure graph worker — #37 / #19

Build temporal supplier/customer/competitor/product/industry/technology/geography exposure relations with provenance, confidence/materiality and historical knowledge times.

Traversal must remain bounded/typed: short default paths, explicit path grammars, top-K/beam limits, hub penalties/materiality decay and path/evidence dedup.

Required tests: path bounds obeyed; future relation evidence absent from earlier cuts; graph expansion cannot explode through hubs; semantic relationships stay distinct from empirically benchmarked transmission values.

### PIT-safe retrieval / analog worker — #19

Implement two separate retrieval problems:

1. evidence retrieval: relevant current evidence after historical knowledge filtering;
2. historical analog retrieval: prior states/episodes whose outcomes were already resolved before the decision cut.

Return shared signal/forecast artifacts rather than introducing a separate execution path.

Required tests: future similar document/state cannot alter earlier retrieval; analog outcome must have resolved before `T`.

### Model / expert workers — #21

Implement local predictive experts that consume frozen provider outputs only. Start with:

- linear/ridge/logistic baselines;
- historical-analog weighted-return predictor;
- LightGBM/XGBoost regression/ranking;
- selected temporal/neural models only when justified by data volume.

Prefer calibrated forecast distributions and cross-sectional ranking. No model executor owns canonical labels or reads unfrozen live data during prediction.

### Meta-weight / strategy-router workers — #21 / #27

Implement inspectable ways of allocating trust across signal/model experts using only outcomes resolved before the current decision cut.

Begin with controls such as:

- static weights;
- exponentially weighted experts;
- rolling prior-OOS weight optimization;
- later Bayesian/context/regime routing.

Preserve the complete attempted strategy/weight genealogy. Do not select only the historically best variant and discard the search history.

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

For each versioned provider/model/strategy/meta/policy:

1. implement against shared contracts;
2. add focused correctness tests plus property/metamorphic/mutation checks only where semantic risk warrants;
3. publish immutable provider/model/strategy/policy identity;
4. assemble requested artifacts into the fixed benchmark;
5. declare explicit arms or a bounded matrix;
6. run with `finance-quant lab run --parallel N`;
7. start/continue its isolated zero-money forward paper account once executable;
8. report exact artifact hashes, arm/strategy IDs, evaluation hash, historical metrics and prospective paper state.

## Search strategy and overfitting control

Do not brute-force all combinations and then crown the historical winner.

Suggested stages:

1. simple technical/static-weight controls;
2. one-provider main effects;
3. competing versions within useful providers;
4. selected interactions;
5. model-family variants on the same provider sets;
6. meta-weight variants trained only on prior resolved OOS outputs;
7. allocation-policy variants on the same forecasts;
8. contextual/regime strategies only after simpler controls exist.

Use `max_arms` to fail accidental Cartesian explosions.

Preserve attempted strategy genealogy and research-trial counts so automated AI coding does not become an invisible backtest-overfitting engine.

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

Correctness gates merges. Predictive/portfolio metrics gate research promotion.

## Audit/export — #39

Do not block useful signal/strategy/forecast/paper loops on RDF infrastructure. Once useful experiment lineages exist, export a Research Evidence Bundle using immutable manifests/ledger plus RDF/JSON-LD, OWL 2, SHACL, PROV-O, deterministic hashing and RO-Crate-style packaging where helpful.

## Safety/holdout

No broker/live capital work. Do not inspect private/sealed holdout contents without explicit authorization. Use development/public historical evaluation plus subsequent realized outcomes for normal iteration.
