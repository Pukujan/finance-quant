# Detailed session handoff — adaptive modular quantitative investment engine

Date: 2026-08-28
Repository: `Pukujan/finance-quant`
Branch: `main`
Purpose: preserve the full architectural/research/product discussion from the long 2026-08-28 design session so a fresh session can continue without relying on chat history.

> This file is a **continuation package**, not a new authority layer. `AGENTS.md`, `docs/CURRENT_STATE.md`, active GitHub issues, shared executable contracts/tests, and explicit human instructions remain the durable authority hierarchy. Where this file records an unresolved correction or open question, the next session should deliberately reconcile the issue/spec before implementation.

---

## 0. Read this first: the most recent conceptual correction

The project should **not** be centered on “build a knowledge sphere/KG and see whether it predicts.”

The most recent and strongest product framing is:

> **Build a local adaptive modular multi-strategy quantitative portfolio engine that continuously estimates which signals, models, strategy families, and allocation policies deserve weight under the current market state; converts those weighted beliefs into an explicit portfolio; executes only zero-money local paper trades; and lets subsequently realized outcomes update/version the system over time.**

Canonical conceptual loop:

```text
MARKET + WORLD DATA
        ↓
INDEPENDENT SIGNAL PROVIDERS
        ↓
VERSIONED SIGNAL VECTOR / FORECASTS
        ↓
META-WEIGHT / ROUTER
        ↓
PREDICTIVE DISTRIBUTIONS / RANKS
        ↓
PORTFOLIO CONSTRUCTION
        ↓
TARGET ASSET WEIGHTS / CASH / TRADE DELTAS
        ↓
LOCAL PAPER EXECUTION
        ↓
REALIZED OUTCOMES
        ↓
UPDATE SIGNAL / MODEL / POLICY CREDIBILITY
        ↺
```

`MarketState`, temporal KG, RAG, news, source epistemics, vendor pre-quantized feeds, fundamentals, macro, momentum, breakout, volatility, technical signals, historical analogs, etc. are **pluggable signal providers**, not the product itself.

This is important because current architecture proposal #35 is titled around the “Temporal Market State Fabric” and may now over-center that subsystem. The next session should **re-evaluate #35/#36 against this latest clarification before coding**, and decide whether to:

1. rename/reframe #35 as the adaptive quantitative engine parent and make Market State a child/provider; or
2. keep #35 as-is but introduce a clearer parent strategy/meta-engine issue and update the north star.

Do not silently proceed as though Market State must be the dominant source of edge.

The system should be perfectly willing to discover that the optimal long-run configuration gives, for example:

```text
KG/RAG                 0%
news                   3%
macro                 12%
momentum              25%
breakout              22%
volatility            10%
analog retrieval       8%
cross-sectional model 15%
cash                  5%
```

or a completely different regime-dependent distribution.

The goal is **not to prove our sophisticated components are useful**. The goal is to let empirical outcomes decide which components deserve weight.

---

## 1. Original project intent and durable constraints

Original conceptual pipeline:

```text
real world information
→ historical PIT truth
→ temporal KG/RAG
→ local learning
→ walk-forward prediction
→ compare predictions with subsequent market prices
→ paper trade
→ inspect everything visually
```

Durable constraints that remain correct:

- configurable paper starting capital;
- persistent local simulated paper accounts;
- real historical and ongoing market data;
- strict point-in-time/bitemporal truth;
- no future price/label leakage;
- historical prices at/before cut `T` may be model input;
- prices/outcomes after `T` are evaluation labels only;
- actual historical temporal knowledge and retrieval where used;
- local model research/training;
- strict walk-forward evaluation;
- simulated/paper execution only;
- visible positions/orders/fills/NAV/PnL/decisions/predictions/evidence;
- chart/realized outcome acts as objective subsequent truth;
- local browser workstation;
- simple Windows/WSL/Docker-friendly operation;
- no broker/live-capital requirement;
- live capital remains out of scope.

The user explicitly rejected a prior assurance-heavy roadmap. Tests/validation exist to make the product correct; assurance must **not** become the product or roadmap.

---

## 2. Current merged software substrate

The working workstation and fixed lab were integrated through PR #34 and merged to `main`.

Important merged product commit:

`9fb53a7974ada959b3ed3bd7d7efe135e6e98848`

Later docs commits included README/handoff refinements. Do not assume this handoff file's commit is the product merge commit.

### 2.1 Existing workstation

Package:

`finance_quant/workstation/`

Key components:

- `data.py` — real daily equity history from Yahoo chart endpoint plus SEC CompanyFacts;
- `model.py` — local standard-library ridge baseline and strict walk-forward construction;
- `paper.py` — persistent `VirtualAccountStore`, next-session-open simulated execution, restart-safe/idempotent paper behavior;
- `app.py` — local browser workstation showing chart, predictions, metrics, paper account and PIT SEC facts.

Run:

```text
python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000
```

### 2.2 Existing empirical result

Real AAPL workflow (2018-01-01 through 2026-08-27):

- 1,988 walk-forward predictions;
- price-only directional accuracy: **53.3702%**;
- price + current small SEC fundamental feature set: **51.8612%**;
- delta: **-1.5091 percentage points**.

This is an important negative result: the current tiny SEC structured feature set **hurt** the price-only baseline. Do not call it a successful KG and do not infer KG predictive value.

Historical simple long/cash cumulative returns from that run were not realistic cost-complete strategy evidence and must not be overclaimed.

Existing paper proof:

- signal on 2026-08-26;
- simulated next-open fill on 2026-08-27;
- BUY 305 AAPL @ 310.61209779052734 including configured slippage;
- marked NAV about $101,210.21 from $100,000.

This proves the local loop `signal -> persist -> simulated next-open fill -> mark`, **not profitability**.

### 2.3 Current Yahoo PIT caveat

The workstation's adjusted Yahoo history is useful for product development but is **not strict raw PIT market truth**, because later corporate actions can retroactively restate adjusted history.

The serious market lane should use:

```text
raw OHLCV
+
separately timestamped splits/dividends/corporate actions
```

and reconstruct historical views as of the decision cut.

This is already owned by #29.

---

## 3. Fixed experiment/lab control plane already exists

`finance_quant.lab` is deliberately the fixed measuring/execution authority.

Existing lab package includes:

- immutable versioned component artifacts;
- content-addressed registry;
- exact component selection by `(lane, artifact_hash)`;
- benchmark assembly with PIT filtering;
- canonical realized outcomes;
- evaluation-content hashing;
- explicit/bounded arm matrices;
- deterministic/parallel execution;
- ExperimentLedger integration;
- full-information scoring;
- prior-resolved-only expert routing;
- independent persistent `ShadowPaperLab` accounts.

Candidate/model/data/KG code must not own:

- future labels;
- canonical historical outcomes;
- benchmark truth;
- PIT cutoff relaxation;
- cost assumptions;
- scoring semantics;
- paper-account truth.

The lab is the referee, not the investment thesis.

Important current correctness evidence from the fixed lab included 23 lab tests and nine targeted semantic mutation probes killed with zero survivors in the dedicated control-plane workflow. The mutations targeted research-invalidating semantics such as future-known PIT filtering, exact component selection, shared outcome coverage, evaluation identity, router no-hindsight timing and shadow-account restart behavior.

Do not rerun or inspect the historical sealed private acceptance/holdout unless a current explicit authorization says to do so.

---

## 4. Existing durable issue tree

Important active issues:

- #12 — master working local predictive quant workstation;
- #27 — versioned knowledge lanes + parallel full-information experiment laboratory;
- #29 — historical PIT data lanes;
- #19 — temporal KG + PIT-safe RAG;
- #21 — local model research/training;
- #18 — continuous local paper refresh;
- #17/#32 — workstation UX/experiment lineage;
- #35 — current architecture proposal: Temporal Market State Fabric + portfolio intelligence;
- #36 — walking skeleton + typed Market IR/API contracts + AI-agent work graph;
- #37 — bounded Market State Fabric: epistemics/trends/claims/exposures;
- #38 — forecast-to-allocation engine + diversified forward paper;
- #39 — reproducible Research Evidence Bundle + semantic provenance export.

Important latest correction: #35/#36 should be re-read before implementation because the product center has shifted from “Market State Fabric as the central engine” to **adaptive modular multi-strategy quantitative portfolio engine**, with Market State as one provider family.

---

## 5. What the product is now

A useful concise name is:

> **Adaptive Quantitative Portfolio Engine**

It has five product layers.

### 5.1 Signal factory

Independent, versioned providers produce predictive signals or forecast distributions.

Possible provider families:

```text
price/momentum
breakout/trend following
volatility
mean reversion
fundamentals
macro vintages
technical indicators
news/event scores
vendor pre-quantized feeds
attention/hype/trends
MarketState
KG/exposure paths
RAG/evidence retrieval
historical analog retrieval
cross-sectional model signals
crypto/on-chain later
prediction-market signals later
```

The critical abstraction should be something like `SignalProvider -> SignalVector/ForecastDistribution` with exact version/provenance/time semantics.

### 5.2 Meta-strategy / weight engine

The system decides which signals/models deserve trust **now**.

There should not be one undifferentiated weight vector. Keep separate:

1. evidence/source weights;
2. individual signal weights;
3. model/expert weights;
4. horizon weights;
5. regime/context-conditioned weights;
6. portfolio/asset weights.

A strategy version can be represented as a complete immutable strategy specification, e.g.:

```text
strategy@v184

signals:
    momentum@v7             weight .18
    breakout@v3             weight .09
    volatility@v4           weight .04
    fundamentals@v5         weight .11
    macro@v3                weight .06
    news_state@v8           weight .12
    trend_hype@v4           weight .08
    kg_exposure@v6          weight .07
    analog_retrieval@v3     weight .10
    cross_section_ranker@v5 weight .15

portfolio:
    policy = robust_mean_variance@v2
    target_vol = ...
    max_position = ...
    max_theme = ...
    cash_allowed = true

execution:
    cadence = ...
    no_trade_band = ...
    cost_model = ...
```

A new strategy version should be able to change one dimension while keeping all others fixed, so performance changes remain attributable.

Candidate weight mechanisms discussed:

- static weights as a control;
- exponentially weighted experts;
- rolling optimization using only prior resolved data;
- regime-conditioned routers;
- Bayesian model averaging/posterior credibility;
- later evolutionary/agent-generated strategy candidates.

The router/meta-engine must never use outcomes unresolved at the decision time.

### 5.3 Forecast synthesis

For instrument `i` at time `t`, models/signals produce expected returns/ranks/distributions. The meta-engine combines them into calibrated predictive distributions rather than only one opaque score.

Prefer:

- cross-sectional ranking where appropriate;
- predicted distributions/probabilities;
- calibration tracking;
- explicit model disagreement;
- uncertainty and missing-data coverage.

Do not treat confidence as one magic `0..1` number.

### 5.4 Portfolio engine

Forecasting is only half the project.

The engine must answer:

- where to invest;
- how much to invest;
- how much cash to hold;
- how much to diversify;
- what to buy/sell/hold;
- whether switching is worth costs;
- when to rebalance;
- when to abstain/no-trade;
- which instrument/venue best expresses a view when alternatives exist;
- how risk/correlation/liquidity/concentration alter raw forecast conviction.

Inputs should include:

```text
per-instrument predictive distributions/ranks
calibration/uncertainty/model disagreement
covariance/correlation/tail-risk estimates
liquidity/spread/slippage/cost estimates
current positions/cash
factor/theme/industry/geography/currency exposures
hard constraints/risk budget
```

Output: immutable `PortfolioIntent` containing at least:

```text
target weights
buy/sell/hold deltas
target cash
expected portfolio return/risk/cost
turnover
binding constraints
rebalance reason
abstention/no-trade state
state/model/forecast provenance
```

Initial competing portfolio policies from #38:

1. equal-weight top-K;
2. edge/confidence-weighted top-K with caps;
3. volatility-scaled / risk-budgeted;
4. mean-variance or robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold.

Portfolio skill and forecast skill must be measured separately.

### 5.5 Local paper + continuous learning

Paper is not a final phase. Every executable credible strategy/policy should begin prospective zero-money history as soon as it can produce a valid decision.

The system accumulates:

```text
immutable prediction
→ immutable PortfolioIntent
→ simulated order/fill
→ actual subsequent price/outcome
→ forecast score
→ portfolio result
→ update future credibility/weights
```

The market supplies the future labels.

---

## 6. Why this is different from a simple breakout bot

During the session the user showed Discord screenshots of a trader describing a 15-minute breakout strategy on gold/Nasdaq, with TradingView backtests, Monte Carlo simulation, a claimed ~43% win rate and ~3.7 profit factor, plus very large live-profit claims.

Conceptual contrast:

Simple breakout system:

```text
price bars
→ breakout rule
→ optional indicator filters
→ entry/exit rules
→ backtest/OOS/Monte Carlo
→ trade
```

Our engine:

```text
many independent signal families
→ multiple model experts
→ context/meta weighting
→ forecast distributions
→ portfolio construction
→ execution
→ realized outcomes
→ weight/version evolution
```

A breakout strategy should not be dismissed. It can be one provider/strategy family inside our system and may outperform much more sophisticated information signals.

Important lesson from the screenshot discussion: win rate is not the objective. A strategy can win only ~43% of trades and still be profitable if average winners are much larger than average losers. We therefore need proper portfolio/economic metrics, not directional accuracy alone.

Potential useful additions to workstation analytics include:

- profit factor;
- average win/loss;
- expectancy;
- drawdown distribution;
- risk of ruin;
- Monte Carlo trade/order reshuffling/path analysis;
- regime-separated results;
- OOS vs forward paper distinction.

---

## 7. Market reality: why tradebots do not make everyone rich

This reality check is important for the next session.

Existing institutional systems do answer many pieces of the problem:

- BlackRock Aladdin: portfolio/risk/scenario/allocation infrastructure;
- RavenPack/LSEG MarketPsych/FactSet/Alexandria: pre-quantized machine-readable news/text/event/sentiment data;
- proprietary quant firms: multi-signal models, meta-models, optimizers, execution and research loops.

What they do **not** publicly provide is a universal correct expected-return function that reliably tells everyone what to buy.

The scarce object is approximately:

```text
E[future return_i | information available now]
```

Reasons winning is hard:

1. active alpha is competitive;
2. once an edge is known/crowded, prices incorporate it earlier and alpha decays;
3. shared datasets are not themselves a moat;
4. transaction costs/slippage/market impact/taxes/borrow reduce gross edge;
5. regime shifts make historical relationships fail;
6. capacity constraints mean an edge can work at small capital and fail at institutional scale;
7. active funds and retail traders often underperform simple benchmarks over long periods;
8. repeated backtesting/search generates false discoveries.

The project is therefore **not guaranteed** to discover alpha. Engineering can be accelerated drastically with AI coding; future market outcomes cannot be fabricated or compressed.

The engine's job is to make research/selection disciplined enough that it does not mistake clever software for economic edge.

---

## 8. The biggest danger: automated overfitting

AI coding makes it cheap to generate thousands/millions of strategy variants.

Naive loop:

```text
generate 100,000 strategies
→ backtest them all
→ choose highest Sharpe
→ paper/trade winner
```

This can become an automated data-mining machine even if no real edge exists.

Therefore the strategy-generation engine must retain **trial genealogy**, not only winners.

Needed discipline:

```text
candidate generation
→ development/training history
→ strict walk-forward predictions
→ experiment/trial accounting
→ untouched/frozen historical holdout where appropriate
→ prospective paper
→ subsequently realized outcomes
→ update credibility
```

Important statistical/research concepts mentioned in the session and worth revisiting:

- Probability of Backtest Overfitting (Bailey et al.);
- Deflated Sharpe Ratio;
- White's Reality Check / data-snooping corrections;
- multiple-testing / factor-zoo problem (Harvey, Liu, Zhu);
- calibration/proper scoring for probabilistic forecasts;
- OOS and regime-conditioned evaluation.

The current private sealed holdout must not be inspected/optimized against unless explicitly authorized.

Forward paper is especially important because it creates future evidence that was impossible to optimize against when the prediction was emitted.

---

## 9. Market State Fabric: still valuable, but subordinate to the engine

The long session explored a “world sphere,” later narrowed to **Temporal Market State Fabric**.

The useful version is:

> reconstruct the smallest economically relevant state for a bounded investment universe, not a literal model of the world.

Initial bounded sphere proposed:

- AI + semiconductors;
- US + China + Taiwan;
- ~50–100 equities/ETFs;
- daily decisions initially;
- 1d/5d/20d horizons.

This remains a strong candidate provider family because it can expose signals that pure price models do not contain.

But it should now be treated as a **signal factory** feeding the adaptive engine, not as the engine's identity.

### 9.1 Living ontology

The session converged on:

```text
stable core ontology
+
versioned domain modules
+
rapidly changing temporal instance graph
```

Ontology describes what kinds of things/relations can exist, e.g. Entity, Company, Country, Product, Technology, Instrument, Industry, Theme, Narrative, MacroVariable, RiskFactor, Event, Claim, Evidence, Exposure.

Temporal graph contains what was believed/known at each time.

Relations may include:

```text
SUPPLIES
CUSTOMER_OF
COMPETES_WITH
SUBSTITUTES_FOR
ENABLES
DEPENDS_ON
OPERATES_IN
EXPOSED_TO
```

Relations should carry:

- valid/effective time;
- `known_at`/knowledge time;
- provenance/source;
- confidence;
- materiality;
- revision/supersession.

Graph traversal must remain bounded: typed paths, short hop counts, top-K/beam limits, hub penalties, materiality decay and dedup.

### 9.2 Epistemic layers

Do not store naked “facts.”

Useful layered model:

```text
SourceArtifact
→ Observation
→ Claim/Proposition
→ Evidence
→ bitemporal EpistemicState
→ MarketBeliefState
→ Derived MarketState
→ BenchmarkedKnowledge
→ PredictiveKnowledge
```

Key distinctions:

- what a source said vs whether it is true;
- factual confidence vs market attention;
- semantic/economic relationship vs empirically observed price transmission;
- historical benchmarked relation vs current forecast;
- claim confidence vs source reliability vs predictive usefulness.

Source ranking should not be one universal score.

Keep dimensions such as:

```text
factual reliability
directness
domain expertise
identity confidence
timeliness
independence
revision transparency
manipulation risk
attention/reach/velocity value
historical incremental predictive usefulness
```

Reliability can later be calibrated by `(source, domain, claim_type)` using only resolutions available before the current decision cut.

Syndicated copies are one independent factual evidence group; propagation volume may still count as attention/hype evidence.

### 9.3 TrendState

Trend/hype should not be one sentiment number.

For any signal `x_t`, retain descriptors such as:

```text
current level
percentile / robust z-score
fast / medium / slow velocity
acceleration
volatility / signal-to-noise
dominant shape
change-point probability
persistence
novelty
saturation
decay rate
source diversity
cross-source confirmation
regime
```

Candidate trend shapes:

- constant/linear;
- exponential;
- logarithmic/saturating;
- logistic/S-curve;
- cyclical;
- spike and decay;
- mean reversion;
- structural break;
- sustained decline.

Hype/narrative lifecycle discussed:

```text
emergence
→ acceleration
→ breakout
→ consensus
→ saturation
→ divergence/decay
→ possible revival
```

Important insight: high attention can be bearish if acceleration/novelty/source diversity are declining and price is already extended. Low absolute attention can be interesting if novelty/velocity/cross-source confirmation are rising from a low base.

---

## 10. Data engineering and compression

The project is substantially a data-engineering problem before it is a modeling problem.

Do not feed the whole internet to a model.

Cascading compression:

```text
huge raw stream
→ relevance filtering
→ duplicate/story clustering
→ entity resolution
→ claims/events/relations
→ trend statistics/state deltas
→ compact state/signal vector
→ model input
```

Data tiers proposed:

```text
Bronze/raw:
  immutable permitted raw evidence, compressed, partitioned, cold

Silver/canonical:
  DocumentCluster, Claim, Event, Entity, Relation, Mention, Source, provenance

Gold/state:
  compact state vectors, active events/relations/trends, deltas/checkpoints

Platinum/model:
  decision_time + instrument + PIT model-ready feature/signal snapshots
```

Use event sourcing/deltas rather than duplicating the full graph continuously.

Predictions should run on scheduled cuts and/or material state changes, with duplicate bursts coalesced/debounced.

Possible idempotency key concept:

```text
(state_hash, model_hash, instrument_id, horizon)
```

---

## 11. We do not need to build all knowledge extraction ourselves

A major scope-reducing realization: many vendors/services already provide **pre-quantized information**.

Examples discussed:

- RavenPack — entity/event/relevance/novelty/sentiment/impact/temporal analytics from large news/source universes;
- LSEG MarketPsych — news/social/text-derived sentiment, buzz, emotion/topic/event time series;
- LSEG Machine Readable News — normalized news + entity/topic/significance/relevance/novelty/sentiment type fields;
- FactSet/Alexandria contextual text analytics;
- GDELT — open world-event/news/entity/theme/co-occurrence streams;
- SEC EDGAR — filings/XBRL with filing timestamps;
- ALFRED/FRED vintages — macro real-time/revision history;
- GitHub/Hugging Face activity — useful AI ecosystem/adoption sensors;
- Coinbase/Polymarket later for cross-asset/event-market data.

New architecture principle:

> `MarketState` should be an integration/temporal-reasoning layer over both raw and pre-quantized sources. It does not matter whether a signal was produced by our LLM or a vendor if it has explicit semantics, version, `known_at`, provenance and can enter the fixed lab correctly.

This means the engine can compare/use:

```text
vendor sentiment
our custom AI-specific state
price/momentum
macro
technical breakout
KG/RAG
```

without forcing us to rebuild RavenPack before testing whether such data matter.

Commercial feeds may be expensive/licensed and should remain optional adapters, not hard architectural dependencies.

---

## 12. OSS reuse strategy

General rule already in `AGENTS.md`:

> upstream pinned dependency -> thin adapter -> constrained extension -> fork only as last resort.

Commodity machinery should come from OSS whenever possible.

Candidate stack discussed:

### Core/fixed semantics

- existing `finance_quant.lab` + ExperimentLedger — keep as fixed PIT/evaluation authority;
- existing `VirtualAccountStore` — authoritative local paper accounting;
- retained/pinned LEAN substrate — multi-asset backtest/execution where useful.

### Data/storage/analytics

- Parquet + ZSTD — compressed immutable analytical artifacts;
- DuckDB — local SQL/Parquet analytics;
- Polars lazy/streaming — efficient transformation pipelines;
- SQLite now / Postgres later if canonical metadata/state complexity warrants it.

### Retrieval

Choose one initially:

- OpenSearch for hybrid lexical + vector retrieval where exact names/numbers matter;
- or Qdrant for lighter vector + strict metadata/time filtering.

Do not deploy both without a concrete reason.

### Models

- LightGBM;
- XGBoost;
- conventional linear/ridge/logistic baselines;
- Qlib as an optional adapter/research framework where it saves work;
- `llama.cpp` or another local LLM runtime for extraction/classification when useful.

### Semantic/audit tooling

- RDFLib;
- pySHACL;
- OWL/PROV/RDF export standards;
- RO-Crate-style packaging;
- CycloneDX/SBOM/ML-BOM concepts where useful.

### Orchestration/ops

- simple local worker processes first;
- OpenTelemetry for engineering/research observability where useful;
- Dagster only when pipeline complexity actually warrants it;
- no Kafka/Kubernetes/distributed lakehouse by default.

---

## 13. The program's portfolio objective is not “highest return”

The engine should optimize long-term capital quality, not merely direction accuracy or raw return.

Conceptually useful objectives include long-term/log wealth subject to drawdown/risk/cost constraints.

Need to decompose returns into:

```text
market beta
factor/risk-premium exposure
timing/allocation value
security-selection alpha
execution value
```

Otherwise the system can “discover” leverage or concentrated beta and mistake it for alpha.

Potential portfolio utility should account for:

```text
long-term growth
max drawdown
tail risk
volatility
turnover
transaction costs
concentration
liquidity
leverage / ruin risk
```

Different users may legitimately prefer different utility/risk parameters, so there may be no universal scalar “best strategy.”

---

## 14. Success criteria

There are multiple levels of success.

### 14.1 Engineering success

The engine:

- reconstructs PIT inputs correctly;
- cannot leak future-known information;
- preserves exact versions/provenance;
- executes deterministic/restart-safe paper accounting;
- exposes missing/degraded data;
- keeps strategy/model/component histories immutable;
- can replay important runs;
- lets multiple agents/modules integrate without semantic drift.

Engineering success is necessary but **not alpha**.

### 14.2 Research success

At least some signal/model/meta-weight combinations demonstrate stable incremental out-of-sample information relative to strong simple alternatives, without depending on one ticker/period/event or obvious hidden leverage.

Useful metrics may include:

- rank IC / cross-sectional ordering;
- calibration/proper score;
- directional/return errors where relevant;
- top-minus-bottom spread;
- stability across regimes;
- contribution/ablation results;
- multiple-testing-aware evidence.

### 14.3 Investment/paper success

Prospective immutable paper portfolios should eventually show useful cost-adjusted behavior relative to declared baselines, with controlled drawdown/concentration/turnover and without hiding behind hindsight.

Forward paper is the strongest prospective empirical benchmark available while live capital remains out of scope.

### 14.4 System-level success

The engine should support adding a materially different signal/domain/asset class without rewriting core evaluation/portfolio semantics.

For example, after the AI/semiconductor information provider exists, a SaaS/energy/crypto/technical-strategy provider should plug in through contracts rather than force a new engine.

### 14.5 Kill criteria

The project must be able to conclude that a sophisticated component is not useful.

If, after adequate PIT-safe OOS/prospective evidence:

```text
KG adds nothing
RAG adds nothing
news adds nothing
MarketState adds nothing
source calibration adds nothing
```

then their active weights can go to zero/removal.

Do **not** respond to negative results by adding complexity automatically.

The most successful final strategy might be unexpectedly simple.

---

## 15. Adversarial failure modes to keep active

Before expanding any layer, remember the hostile pre-mortem.

Major project failure classes:

1. **No economic edge** — richer data/state never improves useful investment outcomes.
2. **Hindsight leakage** — revised articles, later relationships, adjusted prices, revised macro data leak backward.
3. **Fake corroboration** — one underlying source syndicated/reposted hundreds of times becomes false “independent evidence.”
4. **Source-weight circularity** — source gets weighted because model follows it, then model's behavior reinforces the source.
5. **Ontology explosion** — scope turns into modeling every possible concept.
6. **Graph explosion** — everything becomes connected to everything.
7. **LLM semantic pollution** — speculative language becomes fact or modality is dropped.
8. **Regime failure** — historical relationships cease functioning.
9. **Research-process overfitting** — massive automated strategy search finds lucky historical winners.
10. **Forecast-to-portfolio failure** — good predictions generate bad trades because sizing/correlation/costs are wrong.
11. **Execution unreality** — paper fills ignore spread/liquidity/slippage/market hours.
12. **Provider/API failure** — data source disappears, changes semantics, gets paywalled or licensing changes.
13. **OSS drift** — library API/license/serialization/behavior changes.
14. **Operational silent degradation** — feeds disappear or entity resolution fails without crashing, quietly making predictions worse.
15. **Agent/meta-system drift** — orchestration/framework work consumes the roadmap instead of producing investment functionality.

Every new feature should answer:

> What observable experiment or prospective paper evidence will tell us whether this capability adds useful value?

---

## 16. Operational observability and evolution

The system must observe itself.

### 16.1 Engineering telemetry

Useful metrics:

```text
ingest latency
queue depth
failed downloads
processing latency
memory/disk
retrieval/model latency
worker failures
retry counts
```

### 16.2 Semantic/research telemetry

More important:

```text
source coverage/freshness
unknown entity rate
claim contradiction rate
extraction confidence distribution
dedup compression ratio
missing-data rate
state changes/day
model disagreement
prediction calibration
rank IC / forecast error
PnL / NAV / drawdown
turnover / costs
signal decay
regime-specific performance
```

Example silent-degradation alert:

```text
expected sources: 8
active sources:   5
missing: Reuters / SEC / HF
→ data coverage degraded
→ confidence/state coverage downgraded
```

New component/model versions should run champion-vs-candidate, not overwrite history merely because they are newer.

---

## 17. Versioning model

Everything meaningful can evolve independently:

```text
source-adapter@vN
deduplicator@vN
entity-resolver@vN
ontology-module@vN
event-extractor@vN
trend-engine@vN
state-constructor@vN
retriever@vN
signal-provider@vN
forecast-model@vN
meta-router@vN
portfolio-policy@vN
execution-model@vN
```

Need three different identities:

1. semantic/human version;
2. exact code Git SHA;
3. content/artifact identity derived from exact input/config/dependency/ontology/model information.

Old artifacts/results never mutate.

A later extractor/model can disagree with an earlier version; both remain inspectable and testable.

---

## 18. Software architecture and AI coding operating system

Use a **modular monolith with process-isolated heavy workers**, not microservices by default.

Conceptual package areas may eventually look like:

```text
finance_quant/
    evidence/
    signals/
    epistemics/
    ontology/
    graph/
    trends/
    state/
    retrieval/
    models/
    meta/
    portfolio/
    execution/
    lab/
    provenance/
    observability/
    workstation/
```

Conceptual module does not imply network service.

Move something to a true service only for a concrete reason such as independent GPU hardware, scaling, isolation or availability boundary.

### 18.1 Walking skeleton

Current #36 skeleton was:

```text
SourceAdapter
→ CanonicalObservation
→ MarketState
→ ForecastDistribution
→ PortfolioIntent
→ PaperFill
→ CanonicalOutcome
→ Score
→ Workstation
```

Given the newest strategy-centric clarification, the next session should consider generalizing this to avoid making `MarketState` mandatory for every strategy, e.g. conceptually:

```text
Source/Data Inputs
→ SignalProvider(s)
→ Signal/Forecast Artifact(s)
→ MetaWeight/Router
→ ForecastDistribution
→ PortfolioIntent
→ PaperFill
→ CanonicalOutcome
→ Score
→ Weight/Version Update
→ Workstation
```

MarketState can still be one rich provider internally.

Do not change existing fixed lab contracts casually; extend candidate/product contracts around them.

### 18.2 Typed contracts

Important typed objects include or may evolve toward:

```text
SourceArtifact
CanonicalObservation
Claim
Evidence
SignalArtifact / SignalVector
MarketState
ForecastDistribution
StrategySpec
MetaWeightState
PortfolioIntent
PaperFill
CanonicalOutcome
ArtifactRef
```

Cross-process/storage artifacts should have explicit schema/version/time semantics.

### 18.3 Agent work packets

Do not coordinate multiple agents through chat memory.

Machine-readable work packets should specify:

```text
work_id
issue/dependencies
owned files/modules
allowed inputs
required outputs
shared semantics
forbidden authority
acceptance tests
product proof / experiment/paper artifact
exact handoff artifacts
```

Agents must converge on shared contracts rather than invent sibling semantics independently.

### 18.4 Agent/model routing

The session discussed using stronger reasoning/integration models for:

- shared architecture;
- temporal semantics;
- statistical leakage;
- hard debugging;
- cross-module refactors;
- adversarial review;
- experimental methodology.

Parallel/lower-cost workers can handle bounded:

- source adapters;
- normalization;
- fixtures;
- individual signal lanes;
- model executors;
- straightforward tests;
- bounded ontology modules;
- UI panels.

Do not hard-code “Sol always hard / Luna always easy” forever. Track empirical agent performance by task class, CI failures, review corrections, merge success, regression rate and cost/time.

There is no direct Luna connector in the current ChatGPT environment. The repo can be prepared for Luna, but external Luna launch remains external unless a future integration appears.

---

## 19. Verification strategy: high speed without assurance theater

Validation should be proportional to semantic risk.

Suggested stack:

```text
fast static:
  formatter/lint/import rules/strict typing

contracts:
  typed APIs / schemas / serialization round-trips

TDD:
  focused expected behavior

integration:
  permanent walking-skeleton tests

property/invariants:
  rules that must always hold

metamorphic:
  transformed inputs that should preserve/change outputs in known ways

mutation:
  targeted one-character semantic mistakes that could create fake alpha/account corruption

replay:
  deterministic artifact/run reproduction

formal:
  Lean/SMT only for specific hard logical/state constraints

empirical:
  WFO + prospective paper for investment usefulness
```

Important metamorphic examples:

```text
insert irrelevant future article
⇒ earlier prediction/state unchanged

duplicate same underlying Reuters story 100x
⇒ independent factual confidence unchanged
   attention may change

reorder ingestion while preserving identical known_at
⇒ historical state unchanged

add highly similar future retrieval document
⇒ earlier retrieval unchanged
```

Formal theorem proving is useful as a verifier/type-checker for hard semantics, not a stock oracle.

Potential formal targets:

- PIT admissibility definitions;
- accounting identities;
- portfolio hard constraints;
- state-machine/concurrency safety;
- certain graph/path constraints.

Do not formalize stochastic economic hypotheses as theorems.

Correctness gates software merges.

Investment metrics gate **research promotion**, not ordinary software merging.

---

## 20. Epistemic confidence and signal synthesis

Do not average every confidence-like value into one score.

Separate at least:

```text
claim/evidence confidence
market attention/belief
state confidence
exposure/transmission confidence
model predictive probability/distribution
model calibration
historical OOS model credibility
data coverage
model disagreement
execution confidence
```

Claim aggregation can eventually use calibrated Bayesian/log-odds style evidence updates over **independent evidence groups**.

Source reliability itself can be learned hierarchically by `(source, domain, claim_type)`, using only claim resolutions available before decision time.

Model synthesis may use:

- exponentially weighted experts;
- Bayesian model averaging;
- contextual/regime-conditioned routing;
- stacking trained on prior OOS predictions only.

The internal representation should retain uncertainty rather than exposing only an arbitrary 83/100 confidence number.

---

## 21. Research literature/evidence touched during the session

The session checked current literature/vendor evidence to answer whether the broad thesis is plausible.

Supportive/general evidence discussed:

- Tetlock (2007), media pessimism and market activity/returns;
- Engelberg & Parsons, causal influence of media coverage on investor trading;
- Da, Engelberg & Gao, search attention and market behavior;
- FinDKG, dynamic financial KG/news representation for thematic investing;
- temporal KG / graph forecasting literature;
- commercial existence of RavenPack/MarketPsych/Dataminr/AlphaSense/Aladdin as evidence that professional stacks separate information extraction, retrieval, risk and portfolio functions.

Failure/caution evidence discussed:

- Antweiler & Frank: message-board activity had economically small return signal though useful relation to volatility/activity;
- Bailey et al., Probability of Backtest Overfitting;
- White's Reality Check;
- Harvey/Liu/Zhu multiple-testing/factor-zoo caution;
- Deflated Sharpe Ratio;
- regime/non-stationarity literature;
- retail CFD/day-trading loss evidence;
- SPIVA active-manager underperformance/persistence evidence.

Takeaway:

> Information/news/attention effects are real enough to justify research, but signals are noisy, quickly competed away, regime-dependent and extraordinarily easy to overfit. The project is plausible, not proven.

---

## 22. Cross-asset scope

Equities became the first vertical because Yahoo + SEC were convenient real sources, not because the architecture should be equity-only.

Longer-term candidate instrument types:

```text
EQUITY
ETF
CRYPTO_SPOT
CRYPTO_PERP
PREDICTION_MARKET
```

Different asset classes have different outcomes/execution models:

- equity/crypto: future return, excess return, direction/ranking, PnL;
- prediction market: probability change, Brier/log score, settlement accuracy, market PnL.

Cross-asset expansion should occur through shared signal/forecast/portfolio contracts, not a separate engine.

---

## 23. Research paper / product relation

At one point the session discussed whether to build a research paper first and investment bot later.

Correction: **historical research and continuous forward paper should operate together**.

A research paper may eventually be a byproduct/documentation of the system, with prospective paper evidence stronger than backtest-only claims.

Potential high-level research question from the earlier MarketState framing:

> Can a point-in-time reconstruction of economically relevant market/world state improve walk-forward forecasting of future asset outcomes?

Under the newest engine-centric framing, a broader research question becomes:

> Can a local adaptive multi-strategy system learn stable context-dependent weights over heterogeneous signal/model/portfolio policies that improve long-run prospective paper outcomes without succumbing to hindsight or strategy-selection overfitting?

Do not confuse publication-quality evidence with live-capital authority. Live capital remains out of scope.

---

## 24. Immediate next-session decision tree

The next session should **not immediately start building the Market State subsystem**.

First do a short architecture reconciliation.

### Step 1 — read durable truth

Read in order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. this file
4. #35
5. #36
6. `docs/handoffs/LATEST.md`
7. #27 / #29 / #19 / #21 / #38 as relevant
8. existing lab/workstation contracts/tests.

### Step 2 — reconcile the newest product center

Ask:

> Does #35/#36 correctly represent the adaptive multi-strategy engine, or do they still make MarketState mandatory/central?

Recommended likely correction:

```text
Adaptive Quantitative Portfolio Engine
    ├── Signal Provider Framework
    │     ├── price/momentum/breakout/volatility
    │     ├── fundamentals/macro
    │     ├── vendor quantified feeds
    │     ├── MarketState/KG/RAG
    │     └── future signals
    ├── Forecast / Model Expert Framework
    ├── MetaWeight / Context Router
    ├── Portfolio Policy Framework
    ├── Execution / Paper Accounts
    └── Outcome / Learning / Versioning
```

MarketState remains powerful but optional.

### Step 3 — freeze the minimal shared contracts

Likely core cross-agent contracts to settle before fan-out:

```text
SignalProvider / SignalArtifact
ForecastDistribution
StrategySpec
MetaWeightState or RouterState
PortfolioIntent
ExecutionIntent / PaperFill
CanonicalOutcome
ArtifactRef / Version identity
```

Do not redesign existing fixed lab semantics unless a concrete integration incompatibility is proven.

### Step 4 — ensure a strategy can exist without KG/news

Permanent walking skeleton should support a simple technical vertical slice immediately:

```text
raw market data
→ momentum/breakout/volatility signals
→ model/meta weights
→ portfolio policy
→ local paper
→ outcome
```

This proves the engine is not accidentally coupled to the knowledge system.

### Step 5 — then fan out agents

Parallel providers/workers can include:

- raw OHLCV/corporate actions (#29);
- technical strategy provider: breakout/momentum/volatility;
- SEC/macro provider (#29);
- news/vendor-prequantized provider (#29/#37);
- MarketState/trend/epistemics provider (#37);
- KG/RAG/analog provider (#19);
- model/ranker families (#21);
- portfolio-policy variants (#38);
- UI/observability (#32/#17).

Every executable strategy/policy should start prospective local paper history immediately.

---

## 25. Exact prompt to paste into the next ChatGPT session

Use this prompt verbatim or nearly verbatim:

> Continue `Pukujan/finance-quant` from durable repo state, not from assumptions. Read `AGENTS.md`, `docs/CURRENT_STATE.md`, and `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`, then issues #35 and #36 and `docs/handoffs/LATEST.md`. The latest conceptual correction is that the product is an **adaptive modular multi-strategy quantitative portfolio engine**: heterogeneous signal providers → model/meta weights → forecast distributions/ranks → portfolio allocation → local zero-money paper → realized outcomes → weight/version evolution. Market State/KG/RAG/news/vendor feeds are optional signal providers, not the product itself. First reconcile #35/#36/CURRENT_STATE against that correction and tell me exactly what durable issue/contracts need changing; then implement the smallest correct contract/walking-skeleton correction rather than doing more architecture discussion. Preserve fixed `finance_quant.lab` PIT/outcome/scoring/account semantics, keep live capital out of scope, do not inspect the sealed holdout, and make every executable strategy enter forward paper as soon as valid.

---

## 26. Things the next session must not forget

- The user wants the product finished rapidly with AI coding; do not turn “safety/assurance” into months of meta-work.
- However, automated coding increases the danger of automated overfitting and semantic bugs, so contracts + targeted high-value tests are essential.
- Product correctness and investment usefulness are separate authorities.
- Market outcomes, not architecture elegance, decide signal usefulness.
- Negative results are good results and stay in lineage.
- Paper trading is central and continuous, not a deployment afterthought.
- A knowledge graph is not required for the engine to exist.
- Pre-quantized vendor data may replace large amounts of custom extraction.
- Simple technical strategies should be first-class candidate signal providers.
- Cash/no-trade is an explicit allocation choice.
- Diversification should be measured by underlying economic/factor/theme exposure, not ticker count alone.
- “Best strategy” may be regime-dependent and utility-dependent, not one permanent champion.
- Trial count/genealogy must be preserved to defend against strategy-selection overfitting.
- The engine may eventually be more valuable as a research/portfolio system even if no magical alpha source exists.
- The architecture should remain local-first and modular monolith by default.
- Do not claim Luna is running in this ChatGPT environment; the repo only contains Luna-ready handoff/protocol state.
- Do not rerun/inspect the sealed private holdout without explicit authorization.

---

## 27. Final session-state summary

The long session began with a knowledge-centric predictive quant architecture and progressively exposed a larger structure:

1. raw world/market data needs PIT truth;
2. knowledge needs claims/evidence/provenance rather than naked facts;
3. trends need shape/noise/velocity/saturation rather than one sentiment score;
4. forecasting needs calibrated multiple models rather than one oracle;
5. portfolio construction is the missing second half of prediction;
6. forward paper is the strongest prospective benchmark and must start early;
7. sophisticated OSS/vendors already solve many commodity layers;
8. the market makes easy alpha scarce and most active traders/managers do not reliably outperform;
9. AI coding makes experimentation cheap but also makes data-mining/overfitting dramatically easier;
10. therefore the actual product center is the **adaptive modular meta-engine** that learns which signal/model/strategy/allocation components deserve weight, while immutable PIT evaluation and prospective paper keep it honest.

That is the conceptual point at which the next session should resume.
