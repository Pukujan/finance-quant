# Capability assurance policy

Authoritative issue: #14  
Machine contract: `contracts/assurance/capability-assurance-v1.json`

`finance-quant` uses a tiered assurance model. Human approval is a capability/promotion authority, not a replacement for executable evidence. Required gates are conjunctive.

| Phase | Capability | Mandatory assurance summary |
|---|---|---|
| A0 | Bootstrap | SDD/PDD, ordinary regression, repeated determinism, clean environment, non-skippable existing TLA |
| A1 | OSS execution bakeoff | A0-style contracts plus property/stateful, hidden execution cases, mutation, differential/metamorphic, chaos/fault, clean rerun |
| A2 | Autonomous Trader v0 | A1 plus accounting/order state machines, replay, restart/idempotency, hidden cases, mutation thresholds, HITL capability promotion |
| A3 | Multi-session paper | A2-relevant gates plus soak, persistence corruption/recovery, crash-at-boundary campaigns, session-chain invariants |
| A4 | KG observation | Bitemporal KG properties, poisoned future-edge hidden tests, differential/metamorphic retrieval, leakage-guard mutation |
| A5 | KG authority | A4 plus explicit authority invariants, policy-bypass hidden tests, TLA where authority concurrency matters, HITL per escalation |
| A6 | Local learner | PIT/walk-forward/provenance, from-scratch/no-pretrained checks, repeated seeds, calibration/OOD/regime/cost stress, ablation, hidden holdout, HITL |
| A7 | Incremental updates | parent/child differential, rollback, update idempotency, corruption/fault injection, hidden acceptance, repeated reliability, promotion receipt |
| A8 | Shadow/live-readiness | full applicable suite, sealed terminal holdout, operational chaos, soak, TLA authority/promotion, clean no-credential eval, explicit human capital gate |

## Validation families

- **SDD** — explicit behavioral/authority contracts.
- **PDD** — stable property IDs and independent executable oracles.
- **Static/IR** — types, schema checks, temporal effect checking.
- **Property/stateful** — generative and state-machine testing.
- **Hidden acceptance** — exact final cases inaccessible to ordinary implementation/research agents.
- **Mutation** — test/evaluator strength; critical validator target starts at 98% valid-mutant kill rate and no surviving critical invariant-bypass mutant.
- **Differential/metamorphic** — independent reference comparisons and invariant relations.
- **Determinism/clean environment** — repeated independent runs and fresh/containerized reruns.
- **Chaos/fault** — crash, restart, corruption, duplicate/drop/reorder, timeout, resource/dependency failure.
- **Soak** — long-running/multi-session reliability.
- **TLA+** — protocol/authority/concurrency model checking; T3 obligations may not silently skip in authoritative CI.
- **SMT** — selectively adopt for narrow risk/portfolio/IR algebraic constraints when it adds confidence.
- **Lean 4** — selectively prove small stable semantic kernels. Initial candidates remain temporal-checker soundness and pure risk non-widening; do not gold-plate unrelated slices.

## Hidden-holdout rule

Properties and interfaces may be public; exact cases/labels/oracle details that would enable gaming stay isolated. `finance-quant-holdout` remains the sealed quant evaluation boundary. Invocation is receipted and contamination/rotation rules apply.

## Phase completion rule

A phase may not be marked complete/promotable unless every required technique has durable evidence or an explicit, reviewed contract amendment removes the obligation. Aggregate scores cannot hide a failed critical gate.
