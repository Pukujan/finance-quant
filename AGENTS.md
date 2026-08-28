# AGENTS.md — finance-quant operating contract

This repository is a local quantitative research, historical point-in-time evaluation, and zero-capital simulated paper-trading workstation. Agents are implementation/research workers; empirical market outcomes and executable product semantics judge research usefulness.

## Mandatory read order

Before making a material change, read in this order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. the active GitHub master/child issue referenced by current state
4. `docs/handoffs/LATEST.md`
5. relevant contracts/specs and affected implementation/tests

If these sources conflict, resolve the conflict in durable project state before implementation.

## Authority hierarchy

1. Live-capital/safety restrictions in this file and explicit human instructions.
2. Active product issue acceptance criteria and shared public contracts.
3. Executable product-correctness properties/tests for PIT, experiment identity, outcomes, paper accounting, and integration behavior.
4. Implementation details.
5. Research/model/KG outputs.

Research metrics, model output, UI state, agent claims, or framework state never outrank fixed PIT/evaluation/account semantics.

## Hard rules

- Preserve point-in-time semantics: no feature, graph edge, document, universe membership, label, router input, model input, or decision may use information before its legitimate `known_at` time.
- Historical corpus filtering happens before retrieval/ranking/embedding results can influence a decision-time feature or prediction.
- Do not inspect, copy, expose, or optimize against sealed hidden holdout cases/labels unless an explicit current issue grants access.
- Do not add or enable brokerage credentials, live capital, or live order authority. Local simulated paper trading is allowed; broker/live capital remains out of scope.
- Failed, crashed, invalid, rejected, superseded, and losing research attempts remain in durable lineage.
- Never weaken/delete a correctness test merely to make a change pass. If the semantic contract changes, update the durable issue/spec and oracle deliberately.
- A component/model/KG lane may propose predictions; canonical historical snapshots, realized labels, scoring, experiment identity, and paper-account truth are owned by the fixed laboratory/control plane.

## OSS adoption rule

Prefer `upstream pinned dependency -> thin adapter -> constrained extension -> fork only as last resort`.

A local fork requires a concrete product reason and a bounded adapter/patch surface. Do not copy mature frameworks into this repo when a dependency or adapter suffices.

## Vertical-slice rule

New capabilities should be delivered as:

`real/PIT data -> typed component artifact -> experiment arm -> walk-forward/outcome -> evidence/metrics -> workstation visibility`

The frontend is an operator/research surface only. It never owns fills, paper-account truth, historical labels, PIT filtering, experiment identity, or live-capital authority.

## Specification and testing contract

For material capabilities:

- reference the active GitHub issue;
- define or preserve the shared public interface/semantics before or with implementation;
- add the cheapest executable tests that can credibly falsify bugs that would invalidate research or paper execution;
- prefer deterministic unit/integration tests plus property/metamorphic tests for time, replay, cache, DAG, router, and concurrency semantics;
- use targeted mutation testing for critical semantic modules where small operator mistakes could silently corrupt results;
- use small hidden black-box product scenarios only when they add information beyond visible tests;
- use TLA+/SMT/formal methods only for a concrete state-machine/concurrency problem that executable tests cannot credibly cover.

Do not recreate the former assurance-phase ladder as the product roadmap. Tests exist to catch real product/research-integrity bugs, not to grant abstract capability authority.

## Multi-agent implementation rule

The active flywheel architecture is defined by GitHub issue #27 and child issues #28–#32, with #19 owning KG/RAG and #21 owning model research.

Agents/subagents may implement candidate components and models in parallel, but they must converge on shared contracts owned by the laboratory/control plane. Sibling agents must not silently invent incompatible artifact, arm, outcome, router, or paper-account semantics.

Candidate code must not directly construct future labels, relax the knowledge cut, or change scoring/cost assumptions. Those are passed in by the laboratory.

## Session completion / handoff

Before ending a material work session:

1. run the focused correctness/integration tests relevant to the change, plus available CI when useful;
2. record exact commands/results and known failures;
3. update `docs/CURRENT_STATE.md` when semantic project state changes;
4. update `docs/handoffs/LATEST.md` so a fresh worker can continue without chat history;
5. update the active issue with completed work, blockers, and the next exact action when material.

## Current execution direction

The active master product is GitHub issue #12. The working workstation is tracked in #26. The experiment flywheel/control-plane architecture is #27 with implementation lanes #28–#32; #19 is the temporal KG/RAG lane and #21 is local model research.

Current product loop:

`real historical data -> PIT normalization -> versioned knowledge/model components -> parallel walk-forward arms -> canonical realized market outcomes -> full-information scoring/router -> isolated persistent local paper accounts -> browser workstation`

Local simulated paper trading is enabled as a product capability. Broker-hosted paper and live capital are not used. The workstation and fixed laboratory are merged to `main`; the next priority is parallel candidate implementation against #29, #19 and #21 using the stable lab interfaces, followed by objective multi-arm historical/OOS evaluation.
