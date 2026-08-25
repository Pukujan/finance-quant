# AGENTS.md — finance-quant operating contract

This repository is an OSS-backed quantitative research, validation, governance, promotion, and autonomous paper-trading laboratory. Agents are implementation workers, not trading or promotion authorities.

## Mandatory read order

Before making a material change, read in this order:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. the active GitHub master/child issue referenced by current state
4. `docs/handoffs/LATEST.md`
5. relevant ADR/spike/contract/property files
6. affected implementation and tests

If these sources conflict, stop implementation and resolve the conflict in durable project state first.

## Authority hierarchy

1. Capital/safety/holdout restrictions in this file and accepted policy contracts.
2. Machine-readable project and assurance contracts under `contracts/`.
3. Accepted architecture/decision documents and active GitHub issue acceptance criteria.
4. Property catalog and executable oracles.
5. Implementation details.

Tests, UI state, model output, OSS runtime behavior, agent instructions, MLflow state, or research metrics never outrank policy/authority contracts.

## Hard rules

- Preserve point-in-time semantics: no feature, graph edge, universe membership, label, model input, or decision may use information before its legitimate `known_at` time.
- Do not inspect, copy, expose, or optimize against exact sealed holdout cases/labels from `finance-quant-holdout` unless an authorized holdout issue explicitly grants that capability.
- Do not add or enable brokerage credentials, live capital, or live order authority unless a later explicit human authorization issue exists. A passing test/holdout/CI run never grants capital authority.
- Risk may reduce/reject requested exposure; generated code/model/KG/UI/agent logic may not widen risk authority.
- Search/model/KG workers may propose; promotion is a separate authority path.
- Failed, crashed, invalid, rejected, and superseded attempts remain in durable lineage.
- Never weaken/delete an acceptance test merely to make a change pass. If a test is wrong, document the property/spec change and update its oracle deliberately.
- Trading-decision models introduced under issue #21 are from-scratch only: no pretrained weights, embeddings, latent representations, or hidden external model knowledge in the decision path unless a future explicit policy issue changes this rule.

## OSS adoption rule

Prefer `upstream pinned dependency -> thin adapter -> constrained extension -> fork only as last resort`.

A local fork requires a documented upstream blocker, patch inventory, conformance tests, upstream-sync plan, and removal condition. Do not copy a mature framework into this repo and accidentally become its maintainer.

## Vertical-slice rule

New capabilities should be delivered as:

`domain/backend -> typed API/events -> evidence/observability -> thin operator/research UI -> end-to-end validation`

The frontend is an operator/research surface only. It never owns fills, account truth, risk decisions, promotion, holdout access, or capital authority; commands must pass through backend policy/authority gates.

## SDD/PDD change contract

Every material capability/authority change must:

- reference an active GitHub issue and assurance phase (`A0`–`A8`);
- define/update the relevant spec/contract before or with implementation (SDD);
- identify stable property IDs and executable oracles for critical behavior (PDD);
- declare property impact: `PRESERVE`, `STRENGTHEN`, or `CHANGE`;
- add independent tests appropriate to the phase assurance contract;
- update machine-readable project/assurance state when capability status changes;
- update affected human documentation and the session handoff.

## Validation

`contracts/assurance/capability-assurance-v1.json` is the phase assurance authority. Required gates are conjunctive; an aggregate score cannot compensate for a failed critical gate.

Use the cheapest technique that can credibly falsify the property, with deeper methods where required: static/IR checks, unit/regression, property/stateful, hidden acceptance, mutation, differential/metamorphic, repeated determinism, clean environment, chaos/fault injection, soak, TLA+, selective SMT, selective Lean 4, and HITL promotion.

**HITL (`HITL_PROMOTION`) is a capability/promotion gate, not per-trade manual control and not a substitute for automated validation.**

T3/TLA obligations must not silently skip in authoritative CI. Hidden acceptance cases remain hidden. Surviving mutations that bypass a critical invariant are gate failures.

## Session completion / handoff

Before ending a material work session:

1. run every gate required for the active assurance phase that can run in the session/CI;
2. record exact commands, results, known skips, and CI/run links or identifiers;
3. update `docs/CURRENT_STATE.md` when semantic project state changed;
4. create/update `docs/handoffs/LATEST.md` and an append-only dated handoff record;
5. record active issue, branch/base, completed work, decisions, blockers, known failures, and the **next exact action**;
6. ensure a fresh session can continue without relying on chat history.

A session is not considered durably complete if the next worker must ask what the project was trying to do.

## Current execution direction

The active master plan is GitHub issue #12 and the assurance authority is #14. Bootstrap #13 is complete. The active implementation issue is **#15 — A1 NautilusTrader-vs-LEAN execution/runtime conformance bakeoff**. Do not begin Autonomous Trader v0 (#16) until #15 has an explicit runtime disposition and every required A1 gate passes.
