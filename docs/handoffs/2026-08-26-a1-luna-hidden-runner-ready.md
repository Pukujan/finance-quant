# Handoff — A1 Luna hidden runner prepared

Date: 2026-08-26
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1

The public A1 matrix remains green at code baseline `4739392b15319bb209d657294834fed4cfb02d29`. Hidden acceptance remains the only substantive conjunctive blocker. No runtime disposition, paper/live authority, or sealed-holdout access was changed.

A dedicated authorized-runner handoff is now available at `docs/acceptance/A1_LUNA_HIDDEN_RUNNER_HANDOFF.md`. It is written so a local authorized Codex/Luna session can implement the private clean runner without needing hidden-case guidance from the public project.

The handoff pins the public evaluation code baseline to `4739392b15319bb209d657294834fed4cfb02d29` and the production LEAN runtime to commit `185c691b89f28bd68e48d53c02147415134975f0`. It defines a deterministic `git archive` candidate artifact whose exact tar bytes are SHA-256 bound into the `SafeAcceptanceReceipt`.

Before any real seal use, Luna must implement and pass synthetic private tests for credential/network isolation, seal and artifact binding, runtime pinning, use-budget enforcement, one-shot result writing, exact aggregate schema, leakage prevention, finite/unique aggregate metrics, status/failure consistency, crash-before/after-commit behavior, public-verifier round-trip, and log redaction. Real hidden execution must run in an isolated credential-free scorer with read-only sealed/candidate/runtime mounts and no writable path into the public repository.

Public preflight nodes are explicit and real: `tests/test_a1_hidden_acceptance.py`, `tests/test_execution_conformance.py`, `tests/test_execution_differential.py`, `tests/test_execution_faults.py`, `tests/test_execution_lean_a1.py`, `tests/test_execution_metamorphic.py`, and `tests/test_execution_reference.py`, followed by the public receipt verifier CLI.

The only permitted return from Luna is the public `SealRecord`, aggregate-only `SafeAcceptanceReceipt`, candidate artifact SHA-256, and aggregate verifier status. Exact cases, labels, case IDs, expected outputs, traces, counts, or hidden debugging information must never be exported.

## Next exact action

1. Start local Codex/Luna only in an environment explicitly authorized to work with `Pukujan/finance-quant-holdout`.
2. Give it `docs/acceptance/A1_LUNA_HIDDEN_RUNNER_HANDOFF.md` as the controlling implementation/run instruction.
3. Require all synthetic runner tests and public preflight tests to pass before consuming any real seal use.
4. Execute one authorized sealed A1 run in the isolated credential-free scorer and return only the allowed aggregate evidence.
5. Back in the public project, submit the aggregate evidence through `.github/workflows/a1-hidden-acceptance.yml` and require fail-closed verification.
6. Only after hidden acceptance passes and all public gates remain green may issue #15 assign final candidate dispositions or select a primary runtime. Do not begin issue #16 beforehand.
