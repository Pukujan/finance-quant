# A1 Luna Authorized Hidden-Acceptance Runner Handoff

Issue: #15  
Assurance phase: A1  
Prepared from public durable head: `d2d0b24c8ac73e78759732839ae6a12a849b6750`  
Public evaluation code baseline: `4739392b15319bb209d657294834fed4cfb02d29`  
Pinned LEAN runtime commit: `185c691b89f28bd68e48d53c02147415134975f0`

## Mission

Implement and execute the authorized **private** A1 hidden-acceptance runner against the sealed corpus, then export only the public `SealRecord`, aggregate-only `SafeAcceptanceReceipt`, and exact candidate artifact SHA-256 required by `finance_quant.acceptance.a1_hidden`.

The runner is an assurance worker only. It may not select a runtime, promote A1, begin issue #16, or grant paper/live trading authority.

## Authority boundary

The private runner may read sealed material only inside the authorized holdout environment. It must never copy, print, summarize, upload, commit, paste into chat, or expose exact hidden cases, labels, case IDs, payloads, expected values, traces, or oracle internals to `Pukujan/finance-quant`, ordinary logs, GitHub Actions, or public artifacts.

Do **not** execute the real corpus under the standing coarse GitHub PAT. The actual scorer must run in a clean isolated process/container with:

- sealed case set mounted read-only;
- candidate artifact mounted read-only;
- reference/runtime image or dependencies mounted read-only;
- no GitHub, provider, brokerage, MLflow, cloud-general, SSH-agent, or general network credentials;
- network disabled after immutable inputs are staged;
- no writable mount back into the public repository;
- exactly one aggregate result writer.

Luna may implement private runner code in the authorized holdout workspace. The real sealed scoring process itself must satisfy the isolation rules above.

## Public sources Luna must read first

Read from the public evaluation baseline before implementation:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. GitHub issue #15
4. `contracts/assurance/capability-assurance-v1.json`
5. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
6. `contracts/execution/runtime-conformance-v1.json`
7. `docs/acceptance/SEALED_INTERFACE.md`
8. `finance_quant/acceptance/seal.py`
9. `finance_quant/acceptance/a1_hidden.py`
10. `finance_quant/acceptance/uses.py`
11. `tests/test_a1_hidden_acceptance.py`
12. `.github/workflows/a1-hidden-acceptance.yml`

If private instructions conflict with these public authority/receipt constraints, stop without consuming a real seal use and report only the conflict category.

## Exact candidate artifact

Hidden acceptance is bound to immutable public code, not a branch or working tree.

Use public evaluation code baseline:

```text
4739392b15319bb209d657294834fed4cfb02d29
```

From a clean clone, build the deterministic source artifact:

```bash
PUBLIC_EVAL_SHA=4739392b15319bb209d657294834fed4cfb02d29
test -z "$(git status --porcelain --untracked-files=no)"
git cat-file -e "${PUBLIC_EVAL_SHA}^{commit}"
git archive --format=tar --prefix=finance-quant/ "$PUBLIC_EVAL_SHA" > a1-public-candidate.tar
sha256sum a1-public-candidate.tar
```

The lowercase 64-hex SHA-256 of those exact tar bytes is `candidate_artifact_hash`. Rebuild the archive independently in a second clean clone and require the same SHA-256 before opening the sealed corpus. If hashes differ, stop with `CANDIDATE_ARTIFACT_NONDETERMINISTIC`.

Mount the candidate tar or an immutable extraction read-only. Do not substitute the Git commit SHA for the SHA-256 artifact hash.

The scoring environment must independently verify the production LEAN dependency is exactly commit `185c691b89f28bd68e48d53c02147415134975f0`. Any other revision fails closed before hidden execution.

## Seal validation and use budget

Before any real case executes:

1. Locate the authorized A1 sealed set in `Pukujan/finance-quant-holdout` or its approved seal store.
2. Recompute the case Merkle root and labels hash privately.
3. Match both against the public `SealRecord`.
4. Compute `commitment_hash` using the same canonical JSON semantics as `SealRecord.commitment_hash`.
5. Validate the requested `use_number` against `max_uses` before execution.
6. Atomically claim/record the use so crash/retry cannot silently consume another evaluation.

Do not spend a real seal use while developing the runner. Develop and test runner mechanics only with synthetic private fixtures.

## Required private synthetic tests

All must pass before one real sealed run:

1. **Credential isolation** — prohibited credentials or writable public-repo mounts fail before case load.
2. **Network isolation** — scoring requires no network after immutable inputs are staged.
3. **Seal mismatch** — altered synthetic case bytes or labels fail before candidate execution.
4. **Artifact mismatch** — altered candidate bytes fail against the declared artifact SHA-256.
5. **Runtime-pin mismatch** — any non-pinned LEAN revision fails before execution.
6. **Use budget** — use `0`, use `> max_uses`, and reuse of an already-consumed use fail closed.
7. **One-shot writer** — a second write/retry cannot overwrite or append another authoritative receipt.
8. **Exact schema** — receipt contains exactly `case_set_id`, `commitment_hash`, `candidate_artifact_hash`, `status`, `aggregate_metrics`, `failure_classes`, `use_number`.
9. **No leakage** — raw cases, labels, case IDs, payloads, expected values, paths, traces, arbitrary debug objects, and extra fields cannot cross the result boundary.
10. **Metric safety** — metric names are unique/non-empty; values are finite numeric values; no per-case metric arrays are emitted.
11. **Status consistency** — `status=pass` requires empty `failure_classes`; failures use only pre-registered aggregate failure-class names.
12. **Crash before commit** — leaves no authoritative receipt and cannot report pass.
13. **Crash after commit** — preserves exactly the committed receipt; restart cannot create a second authoritative result for the same use.
14. **Public verifier round-trip** — synthetic matching pass verifies; mismatched seal/hash/use/status, extra fields, duplicate or non-finite metrics, and non-empty pass failures all fail closed.
15. **Log redaction** — stdout, stderr, exceptions, test reports, and retained artifacts do not contain synthetic raw case/label payloads; production uses the same aggregate-only output boundary.

The private suite must cover the public A1 hidden classes already registered by issue #15 and `runtime-conformance-v1.json`, without exporting exact cases, counts, or new hints derived from failures.

## Public preflight — exact test nodes

Run against the extracted public candidate before opening the sealed suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest \
  tests/test_a1_hidden_acceptance.py \
  tests/test_execution_conformance.py \
  tests/test_execution_differential.py \
  tests/test_execution_faults.py \
  tests/test_execution_lean_a1.py \
  tests/test_execution_metamorphic.py \
  tests/test_execution_reference.py \
  -q
python -m scripts.verify_a1_hidden_acceptance --help
```

Any failure is a blocker. Do not modify a public test, execution oracle, PIT boundary, or permitted-difference rule merely to continue the hidden run.

## Real sealed execution

Only after all synthetic runner tests and the public preflight are green:

1. Start a fresh isolated scorer.
2. Verify prohibited credentials are absent and network is disabled.
3. Mount one sealed case set read-only.
4. Mount the exact candidate artifact read-only.
5. Mount the reference/runtime environment read-only and verify the LEAN pin.
6. Revalidate seal commitments and candidate SHA-256.
7. Atomically claim the next permitted use.
8. Execute the full registered A1 hidden corpus once.
9. Aggregate internally.
10. Commit exactly one `SafeAcceptanceReceipt` through the one-shot writer.
11. Export only the public `SealRecord`, aggregate-only receipt, and candidate artifact hash.
12. Destroy the scoring workspace and uncommitted case-level output.

## Required public schemas

`SealRecord` contains exactly:

```json
{
  "case_set_id": "...",
  "case_merkle_root": "<64 lowercase hex>",
  "labels_hash": "<64 lowercase hex>",
  "sealed_at": "...",
  "eval_harness_sha": "...",
  "scorecard_ref": "...",
  "max_uses": 2
}
```

Use the actual authorized `max_uses`; the value above is illustrative only.

`SafeAcceptanceReceipt` contains exactly:

```json
{
  "case_set_id": "...",
  "commitment_hash": "<64 lowercase hex>",
  "candidate_artifact_hash": "<64 lowercase hex>",
  "status": "pass|fail|invalid",
  "aggregate_metrics": [["metric_name", 0.0]],
  "failure_classes": [],
  "use_number": 1
}
```

Do not add timestamps, case counts, per-case scores, fixture names, paths, labels, stack traces, or debug metadata.

## Mandatory public verifier round-trip

Before returning evidence, use a clean public checkout of the evaluation baseline:

```bash
python -m scripts.verify_a1_hidden_acceptance \
  --seal-record /path/to/public-seal-record.json \
  --safe-receipt /path/to/safe-receipt.json \
  --candidate-artifact-hash '<64 lowercase hex>'
```

A successful verification retains `authority: NONE`. Any nonzero exit is a blocker; never edit the verifier or receipt to manufacture a pass.

Then submit the same three public values to `.github/workflows/a1-hidden-acceptance.yml`. That workflow is only an aggregate verifier; it must never receive holdout credentials or sealed files.

## Failure behavior

If hidden acceptance returns `fail` or `invalid`:

- preserve only the aggregate receipt and authorized aggregate failure classes;
- do not reveal failed cases, values, labels, expected outputs, counts, or traces;
- do not rerun automatically;
- do not use another seal invocation as an iterative debugger;
- return control to issue #15 with the unchanged public contract.

Runner defects must be repaired using synthetic fixtures before any further authorized real invocation.

## Completion response Luna may return

Return only:

```text
A1 hidden runner: COMPLETE | BLOCKED
public_eval_sha: 4739392b15319bb209d657294834fed4cfb02d29
candidate_artifact_hash: <sha256 or NONE>
seal_record: <public aggregate JSON or NONE>
safe_acceptance_receipt: <public aggregate JSON or NONE>
public_verifier: PASS | FAIL_CLOSED | NOT_RUN
notes: <aggregate-only operational note; no sealed details>
```

Do not select a runtime, close issue #15, begin issue #16, or enable any trading authority. The public project performs final conjunctive-gate verification and candidate disposition after receipt ingress.