# Handoff — A1 LEAN production candidate probe

Date: 2026-08-25  
Branch: `bootstrap/oss-autonomous-trader-replatform`  
Active epic: #12  
Active issue: #15  
Assurance phase: A1  
Project status: `A1_LEAN_DIFFERENTIAL_SLICE`

## Completed this session

- Re-read the required durable authority chain before mutation: `AGENTS.md`, `docs/CURRENT_STATE.md`, active issue #15, this handoff, and `contracts/assurance/capability-assurance-v1.json`; also re-read the A1 SDD/PDD and executable runtime contract before fixing the candidate harness.
- Found that the branch had advanced to a credential-free production LEAN fill-model probe: exact source pin `185c691b89f28bd68e48d53c02147415134975f0`, direct `EquityFillModel.MarketOnOpenFill` execution, finance-quant normalization/differential verification, and three-run candidate CI.
- Verified first candidate-probe head `24976efc7587f83175e24442f281b9a4b7b577b3`: ordinary tests `32875746688` **PASS**, Phase-B `32875746634` **PASS**, while A1 runtime-candidates `32875746733` **FAIL** only in `Run three deterministic candidate probes`; LEAN checkout, exact pin/license verification, .NET setup, and production probe build all passed.
- Compared the probe harness against the pinned upstream LEAN implementation/tests and found a concrete harness defect: LEAN `Order.Time` is UTC and upstream constructs `MarketOnOpenOrder` with a UTC-converted submission instant, while the finance-quant probe supplied an unqualified New York-local wall-clock `DateTime`.
- Fixed that mismatch in commit `6e21bc0fc51f29124ada8eef7c925be88d3975fc`: the decision instant is converted to UTC before constructing `MarketOnOpenOrder`; no oracle, timing rule, fill expectation, or authority gate was relaxed.
- Strengthened failure evidence in commit `57758d7d8ab81c1e6445ec42ec970c2b1c788d91`: candidate stdout/stderr are retained and uploaded even when the probe fails, while a nonzero probe status still fails the workflow before semantic conformance can be claimed.
- Updated `docs/CURRENT_STATE.md` with the production-probe slice, exact failure, root-cause fix, current CI state, and next exact action.

No runtime disposition was made. Trading authority remains **NONE**; autonomous paper trading and live capital remain **DISABLED**; sealed-holdout exact cases/labels were not accessed.

## Validation status

Implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91` triggered a fresh exact-head validation cycle. A1 runtime-candidates run `32876861792` was still **IN_PROGRESS** when this handoff was written; exact-head Phase-B and ordinary bootstrap/test workflows were also re-running. Therefore this handoff does **not** claim the UTC fix is validated yet.

The previous failing run remains useful evidence: build/pin/license succeeded and the failure was isolated to execution/verification, which is why the harness was corrected instead of weakening the differential contract.

A1 is still **IN_PROGRESS** and its gates remain conjunctive. NautilusTrader candidate evidence, hidden acceptance, mutation thresholds, broader metamorphic coverage, complete deterministic/clean-environment receipts, and chaos/fault campaigns remain outstanding.

## Next exact action

1. Re-read the authority chain and recheck exact implementation head `57758d7d8ab81c1e6445ec42ec970c2b1c788d91` GitHub Actions. If runtime-candidates fails, inspect the preserved `a1-lean-production-fill-probe` diagnostics and fix the harness/runtime integration without weakening `assert_normalized_receipts_conform`, the three-run requirement, or any PIT/authority invariant.
2. If the LEAN candidate workflow passes, record the exact run and three-run raw/evidence equivalence, then implement the thin credential-free **NautilusTrader** candidate adapter/evidence for exactly the same public daily-bar subset and comparison classes.
3. Continue hidden/mutation/metamorphic/determinism/clean-env/chaos A1 evidence for both candidates before any disposition.
4. Do not select a primary runtime or start #16 until every required A1 gate is green.

Do not enable paper/live capital authority and do not inspect sealed-holdout exact cases/labels.

Append-only record: `docs/handoffs/2026-08-25-a1-lean-production-probe.md`.
