# Luna candidate implementation protocol

This file is an execution brief for a multi-agent implementation runner. The fixed laboratory in `finance_quant.lab` is already the benchmark/execution/scoring authority. Candidate agents should build useful historical knowledge/model components against it, not redesign it locally.

## Start here

Read:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. `docs/handoffs/LATEST.md`
4. issues #27, #29, #19, #21
5. `finance_quant/lab/`
6. `tests/test_lab_*.py`

## Shared interfaces to preserve

Do not change these inside a candidate workstream unless a concrete integration bug requires a centrally coordinated change:

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

## Parallel worker lanes

Spawn these independently where possible.

### Market worker — #29

Build raw OHLCV plus separately timestamped splits/dividends/corporate actions. Produce strict PIT market features without relying on retrospectively adjusted history as source truth.

Required product tests: future corporate action cannot alter an earlier raw historical view; reconstruction is deterministic; source revisions/versioning remain inspectable.

### SEC/document worker — #29 / #19

Ingest historical filing text, filing timestamps, amendments and structured facts. Emit PIT temporal observations and document/provenance references.

Required product tests: filing/amendment is unavailable before its public filing time; later amendment does not rewrite earlier historical snapshot.

### Macro worker — #29

Implement historical-vintage macro observations, preferably ALFRED-style vintages where available. Preserve release/revision times.

Required product test: revised macro values cannot leak into earlier cuts.

### News/event worker — #29 / #19

Ingest historical financial news/events with publication/first-seen timestamps, entity resolution and syndicated-story dedup. Produce versioned news/hype/event artifacts.

Required product tests: future article cannot affect earlier cut; duplicated syndication does not become independent evidence; changing extractor version creates a new artifact without mutating the old one.

### Industrial graph worker — #19

Build temporal supplier/customer/competitor/product/industry/event relations with provenance, confidence/materiality and historical knowledge times.

Traversal must be bounded/typed. Default to short paths; use explicit path grammars, top-K/beam limits, hub penalties/materiality decay and path/evidence dedup.

Required product tests: traversal depth/path grammar/top-K are obeyed; hub explosion is bounded; future relation evidence cannot enter earlier cuts.

### PIT-safe RAG worker — #19

Retrieval corpus selection must apply historical knowledge filtering **before** vector/graph ranking. Return evidence IDs/provenance with retrieved context.

Required product test: adding a highly similar future document cannot change retrieval for an earlier cut.

### Model workers — #21

Implement several local predictive executors that consume only `ArmContext`/frozen inputs. Start with interpretable linear/logistic models, tree/boosting/ranking families, then selected temporal/neural families where useful.

No model executor should own canonical realized labels or read unfrozen live data directly during prediction.

## Candidate publication flow

For every component version:

1. create a `ComponentSpec` JSON;
2. create a temporal-observation payload using the standard schema;
3. publish with `finance-quant lab publish-component`;
4. preserve returned artifact hash;
5. assemble requested artifacts into a fixed benchmark;
6. declare explicit arms or a bounded matrix;
7. run with `finance-quant lab run --parallel N`;
8. report exact artifact hashes, arm IDs, evaluation hash and objective results.

## Matrix strategy

Do not brute-force every possible lane combination immediately.

Use stages:

1. price baseline;
2. one-lane main effects;
3. competing versions within each useful lane;
4. selected pair interactions;
5. selected combined KG/RAG arms;
6. model-family variants on promising information sets;
7. contextual router/ensemble;
8. forward shadow paper for survivors.

Use `max_arms` to make accidental Cartesian explosions fail explicitly.

## Completion report for each worker

Return:

- exact files/commits changed;
- component spec and returned artifact hash(es);
- lane/version semantics;
- data source/time semantics;
- tests added and results;
- candidate arm/matrix additions;
- experiment/evaluation hashes;
- OOS results, including negative results;
- known limitations.

Do not describe an information lane as useful merely because its software tests pass. Predictive usefulness is determined by unseen realized market outcomes.

## Safety/holdout

No broker/live capital work. Do not inspect private/sealed holdout contents without explicit authorization. Use fixed public/development historical evaluation sets plus subsequent realized market outcomes for normal iteration.
