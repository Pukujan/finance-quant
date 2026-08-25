# Handoff — A0 complete, A1 ready

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Base: `main@cdf69afadf473359d0eb6d4db3d18cbc96c03d32`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `BOOTSTRAP_COMPLETE`

## Goal reached

The governance/resumability/assurance bootstrap (#13 / A0) is complete. The repository is now durably pointed at issue #15: the NautilusTrader-vs-LEAN execution/runtime conformance bakeoff.

No autonomous trader, brokerage authority, paper-trading authority, or live-capital authority was introduced during bootstrap.

## A0 validation evidence

Validated implementation head before the semantic A0→A1 state-transition edits:

`b01e9be2c6dd9eb27a1189dc5454f0e7a61db2ef`

Successful workflow runs on that head:

- `tests` run `32850720334`: full pytest + smoke — PASS.
- `phase-b` run `32850720245`: Phase-B benchmark + 3-run determinism drill + `verify --phase-b` — PASS.
- `bootstrap-assurance` run `32850720179`:
  - bootstrap/project contracts — PASS;
  - generated README status freshness — PASS;
  - property catalog/oracle validation — PASS;
  - pinned TLA2Tools/TLC promotion-ladder model check — PASS, non-skippable;
  - Windows full regression — PASS;
  - smoke — PASS;
  - 3-run determinism drill — PASS;
  - preserved Phase-B verifier — PASS;
  - isolated fresh-venv install/test/verify — PASS.

The final A0→A1 state-transition commit must also pass the repository CI before PR #24 is merged.

## Defects found and fixed by A0 gates

The gates found real defects; none were bypassed or weakened:

- legacy TLA+ syntax that had previously been hidden by a skip path;
- promotion protocol allowing an already-approved immutable candidate identity to re-enter promotion;
- fresh-environment drill installing dependencies but not the project package, breaking subprocess workers;
- generated README freshness check depending on platform line endings;
- B1–B5 receipts embedding repository-relative assumptions that failed for temp drill paths;
- LEAN receipts embedding per-run absolute temp paths, breaking deterministic receipt equality.

## Durable decisions

- `finance-quant` owns policy, contracts, evidence, validation, promotion, PIT semantics, and risk authority.
- Mature OSS owns replaceable machinery behind thin adapters.
- Future product capabilities are vertical slices: domain/backend → typed API/events → evidence/observability → thin operator/research UI → E2E validation.
- Frontend authority remains `OPERATOR_ONLY`.
- Sealed holdout exact cases/labels remain inaccessible to ordinary agents.
- Required assurance gates are conjunctive; a failed critical invariant cannot be averaged away.
- A2 Autonomous Trader v0 (#16) cannot begin until A1 (#15) has an explicit runtime disposition and all A1 gates pass.

## A1 required assurance

Issue #15 is governed by A1 and requires: SDD, PDD, static/IR validation, unit/regression, property/state-machine tests, hidden acceptance, mutation testing, differential testing, metamorphic testing, repeated determinism, clean-environment validation, and chaos/fault injection.

## Known blocker outside repository code

`main` branch protection / required-check enforcement is tracked in issue #25. The available GitHub connector did not expose a branch-protection/ruleset write operation, so do not claim server-side protection is enabled until #25 is resolved through an admin-capable surface.

## Next exact action

Start **issue #15** by writing the A1 execution-runtime conformance SDD/PDD contract before installing/selecting either runtime.

The first A1 artifact should define one shared semantic fixture and normalized receipt contract covering at least:

1. clock/event ordering and same-bar rules;
2. order lifecycle, cancellation, rejection, partial fills, duplicate events and idempotency;
3. fees, spread/slippage and cost stress;
4. account/position/cash/NAV invariants;
5. PIT data boundary and no-future-information rules;
6. restart/recovery and persisted state;
7. hidden execution cases and mutation targets;
8. differential comparison rules for NautilusTrader vs LEAN;
9. chaos/fault scenarios;
10. deterministic repeated-run evidence.

Only after the contract/oracles exist should the next session add thin NautilusTrader and LEAN adapters and execute the bakeoff.

## Read next

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. GitHub #12, #14 and active #15
4. this handoff
5. `contracts/assurance/capability-assurance-v1.json`
6. existing execution/IR/property contracts and reference interpreter

Do not start #16 in this session unless #15 is explicitly completed and promoted by durable project state.
