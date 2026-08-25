# Current project state

<!-- MACHINE-STATE: architecture=OSS_FIRST_AUTONOMOUS_TRADER_REPLATFORM status=BOOTSTRAP_IN_PROGRESS assurance=A0 active_issue=13 -->

## Active direction

The active master plan is GitHub issue **#12 — OSS-first autonomous trader + visual research console**.

Current work is **#13 — governance/resumability/CI/docs bootstrap**, governed by assurance phase **A0** in issue #14 and `contracts/assurance/capability-assurance-v1.json`.

The old Phase-B execution plan (#11) is **PARKED**. Its PIT, IR, property catalog, sealed holdout, mutation-hardening, deterministic rerun, reference-interpreter, TLA+, LEAN/Qlib, and evidence assets remain preserved as legacy baselines/oracles. Do not treat #11 as the active sequencing authority.

## Current capability

- Trading authority: **NONE**
- Autonomous paper trading: **DISABLED**
- Live capital: **DISABLED**
- Frontend: roadmap/vertical-slice policy only; **OPERATOR_ONLY** authority
- Sealed holdout: remains isolated; ordinary agents may not inspect exact cases/labels

## Bootstrap deliverables in progress

- durable issue hierarchy #12–#23;
- root `AGENTS.md`;
- machine project state under `contracts/project/`;
- machine capability assurance matrix under `contracts/assurance/`;
- durable session handoff under `docs/handoffs/`;
- deterministic README project-status generation/checking;
- bootstrap contract validation CI;
- non-skippable TLA/TLC CI for T3 obligations;
- repeated deterministic/full/fresh-environment validation.

## Next exact action

Get the bootstrap pull request green under **every A0 gate**. Fix any failures without weakening properties/tests. Once bootstrap is merged and durable state is updated to `BOOTSTRAP_COMPLETE`, the next implementation issue is **#15 — NautilusTrader vs LEAN execution/runtime conformance bakeoff (A1)**.

Do **not** begin Autonomous Trader v0 (#16) before #15 selects the runtime and produces A1 evidence.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. GitHub issue #12 and the active child issue
4. `docs/handoffs/LATEST.md`
5. `contracts/assurance/capability-assurance-v1.json`
6. relevant property catalog/specs/tests
