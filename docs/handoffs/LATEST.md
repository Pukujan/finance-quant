# Handoff — A1 Luna hidden runner prepared

Date: 2026-08-26
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1
Master plan: #12
Bootstrap status: BOOTSTRAP_COMPLETE

The public A1 code baseline `4739392b15319bb209d657294834fed4cfb02d29` remains fully green across the required public matrix. Runtime selection remains `NONE / PENDING`; trading authority remains `NONE`; autonomous paper/live execution remains disabled; sealed-holdout contents were not accessed in this public preparation session.

The remaining substantive A1 blocker is genuine `HIDDEN_ACCEPTANCE`. A dedicated authorized-runner implementation/run handoff now exists at `docs/acceptance/A1_LUNA_HIDDEN_RUNNER_HANDOFF.md`.

That handoff pins the exact public evaluation baseline and LEAN runtime commit, defines deterministic candidate artifact hashing, specifies the credential-free read-only scoring boundary, enumerates the synthetic private tests required before a real seal use, pins the exact public preflight test nodes, defines exact allowed public output schemas, and requires a clean public-verifier round-trip before evidence is returned.

The local authorized Codex/Luna session may implement runner mechanics inside `Pukujan/finance-quant-holdout`, but the actual sealed scorer must have no GitHub/provider/brokerage/MLflow/general-network credentials and may export only the public `SealRecord`, aggregate-only `SafeAcceptanceReceipt`, and candidate artifact SHA-256. It must not expose exact cases, labels, case IDs, expected outputs, traces, counts, or hidden debugging information.

No real seal use should be consumed while developing the runner. Synthetic private fixtures must close runner mechanics first. A failed/invalid real hidden result must be returned only as aggregate evidence and must not trigger an automatic second run.

## Next exact action

1. Launch local Codex/Luna in an environment explicitly authorized for `Pukujan/finance-quant-holdout` and give it `docs/acceptance/A1_LUNA_HIDDEN_RUNNER_HANDOFF.md` as the controlling instruction.
2. Require every synthetic private runner test and the explicit public preflight suite to pass before consuming a real seal use.
3. Execute one authorized sealed A1 run in the isolated credential-free scorer and return only the permitted aggregate evidence.
4. Submit the public seal/receipt/hash through `.github/workflows/a1-hidden-acceptance.yml` and require `finance_quant.acceptance.a1_hidden` to verify fail-closed.
5. Only after hidden acceptance passes and every public A1 gate remains green may issue #15 assign final dispositions and select a primary runtime. Do not begin issue #16 beforehand.

Append-only record: `docs/handoffs/2026-08-26-a1-luna-hidden-runner-ready.md`.
