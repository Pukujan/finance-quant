# AGENTS.md — finance-quant operating contract

This repository is a local quantitative research, historical point-in-time evaluation, and zero-capital simulated paper-trading workstation. Agents are implementation/research workers; empirical market outcomes and executable product semantics judge research usefulness.

## Mandatory read order

Before making a material change, read in this order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. the active GitHub master/architecture/child issue referenced by current state
4. `docs/handoffs/LATEST.md`
5. relevant contracts/specs and affected implementation/tests

If these sources conflict, resolve the conflict in durable project state before implementation.

## Authority hierarchy

1. Live-capital/safety restrictions in this file and explicit human instructions.
2. Active product/architecture issue acceptance criteria and shared public contracts.
3. Executable product-correctness properties/tests for PIT, experiment identity, outcomes, paper accounting, portfolio intent, and integration behavior.
4. Implementation details.
5. Research/model/KG/state outputs.

Research metrics, model output, UI state, agent claims, or framework state never outrank fixed PIT/evaluation/account semantics.

## Hard rules

- Preserve point-in-time semantics: no feature, graph edge, document, claim, source score, universe membership, label, router input, model input, portfolio decision, or paper action may use information before its legitimate `known_at` time.
- Historical corpus filtering happens before retrieval/ranking/embedding results can influence a decision-time state, feature or prediction.
- Do not inspect, copy, expose, or optimize against sealed hidden holdout cases/labels unless an explicit current issue grants access.
- Do not add or enable brokerage credentials, live capital, or live order authority. Local simulated paper trading is allowed; broker/live capital remains out of scope.
- Failed, crashed, invalid, rejected, superseded, and losing research attempts remain in durable lineage.
- Never weaken/delete a correctness test merely to make a change pass. If the semantic contract changes, update the durable issue/spec and oracle deliberately.
- A component/model/KG/state/portfolio lane may propose outputs; canonical historical snapshots, realized labels, scoring, experiment identity, and paper-account truth are owned by the fixed laboratory/control plane.
- Do not collapse factual confidence, market attention, economic materiality, exposure strength and predictive usefulness into one generic confidence number.

## OSS adoption rule

Prefer `upstream pinned dependency -> thin adapter -> constrained extension -> fork only as last resort`.

A local fork requires a concrete product reason and a bounded adapter/patch surface. Do not copy mature frameworks into this repo when a dependency or adapter suffices. Do not introduce distributed infrastructure merely because the architecture could scale someday; local workload must justify it.

## Vertical-slice rule

New capabilities should be delivered as:

`real/PIT data -> typed canonical artifact/state -> experiment arm -> forecast/portfolio intent -> walk-forward/outcome -> forward paper -> evidence/metrics -> workstation visibility`

The frontend is an operator/research surface only. It never owns fills, paper-account truth, historical labels, PIT filtering, experiment identity, or live-capital authority.

## Specification and testing contract

For material capabilities:

- reference the active GitHub issue;
- define or preserve the shared public interface/semantics before or with implementation;
- add the cheapest executable tests that can credibly falsify bugs that would invalidate research or paper execution;
- prefer deterministic unit/integration tests plus property/metamorphic tests for time, replay, dedup, cache, DAG, router, portfolio and concurrency semantics;
- use targeted mutation testing for critical semantic modules where small operator mistakes could silently corrupt results;
- use small hidden black-box product scenarios only when they add information beyond visible tests;
- use Lean/SMT/formal methods only for a concrete hard invariant/state-machine/constraint problem that executable tests cannot credibly cover.

Do not recreate the former assurance-phase ladder as the product roadmap. Tests exist to catch real product/research-integrity bugs, not to grant abstract capability authority.

Correctness gates software merges. Noisy alpha/performance metrics ordinarily gate research promotion rather than code merging.

## Multi-agent implementation rule

The active architecture proposal is #35. The fixed experiment flywheel remains #27/#28–#32. #29 owns PIT data lanes, #37 the bounded epistemic/trend Market State Fabric, #19 KG/RAG, #21 model research, #38 portfolio allocation, and #39 audit export.

Before the broad candidate fan-out, #36 freezes the walking-skeleton/API/MarketIR/PortfolioIntent/work-packet boundaries enough for sibling agents to work safely.

Agents/subagents may implement candidate components and models in parallel, but they must converge on shared contracts owned by the laboratory/control plane. Sibling agents must not silently invent incompatible artifact, state, arm, outcome, router, portfolio-intent, or paper-account semantics.

Candidate code must not directly construct future labels, relax the knowledge cut, or change canonical scoring/cost assumptions. Those are passed in by the laboratory.

Every agent work packet should declare dependencies, owned modules/files, typed inputs/outputs, forbidden authority, focused acceptance tests and required product proof/experiment arm.

Use capability-based routing rather than permanent model roles: stronger reasoning/integration workers handle shared temporal/statistical/architecture problems; bounded adapters/features/models/tests/UX can fan out to parallel workers. Track which agents perform best by task class, review correction and regression rate.

## Session completion / handoff

Before ending a material work session:

1. run the focused correctness/integration tests relevant to the change, plus available CI when useful;
2. record exact commands/results and known failures;
3. update `docs/CURRENT_STATE.md` when semantic project state changes;
4. update `docs/handoffs/LATEST.md` so a fresh worker can continue without chat history;
5. update the active issue with completed work, blockers, empirical results and the next exact action when material.

## Current execution direction

The active master product is #12. The durable architecture proposal is #35.

Current north-star loop:

`world data -> PIT evidence -> epistemic/market state -> exposure/retrieval -> forecast distributions -> portfolio allocation -> local zero-money paper -> realized outcome -> learning`

The implementation is a modular monolith with process-isolated heavy workers. The initial bounded sphere is AI + semiconductors across US/China/Taiwan. Forward paper is a continuous benchmark from the first executable arm/policy, not a later deployment phase.

Immediate order:

1. freeze #36 shared walking-skeleton/API/MarketIR/PortfolioIntent/work-packet contracts and CI tiers;
2. resume #29/#37/#19/#21 vertical slices in parallel behind those contracts;
3. feed forecasts into #38 competing allocation policies and isolated forward paper accounts;
4. surface evidence/state/forecast/allocation/fills/results in #32/#17;
5. add #39 standards-based audit export after useful lineages exist.

Local simulated paper trading is enabled. Broker-hosted paper and live capital are not used.
