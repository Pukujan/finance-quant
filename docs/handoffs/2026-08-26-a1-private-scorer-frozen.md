# A1 private scorer package frozen before real seal use

Date: 2026-08-26
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #15
Assurance phase: A1
Starting public head: `9fee59cc5a05555d6823c8d7e1a6f0da91fde275`
Frozen public evaluation baseline: `4739392b15319bb209d657294834fed4cfb02d29`
Candidate artifact SHA-256: `ed2b7b335f4be0f256fc7b28b8df12ae0a337c7b2bdec0c9925ddcd9bef630ff`
Pinned LEAN runtime: `185c691b89f28bd68e48d53c02147415134975f0`
Private scorer package SHA-256: `385a95ee8d35eb6264b1c67026d4355ba25fe80026eaad11fed68055a977924f`

## Public validation

Starting public head `9fee59cc5a05555d6823c8d7e1a6f0da91fde275` completed all eight PR-triggered workflows successfully: tests `32967846456`, legacy Phase-B `32967846563`, bootstrap-assurance `32967846446`, runtime-candidates `32967846425`, Nautilus callback evaluator `32967846467`, Nautilus pre-open evaluator `32967846473`, `a1-assurance` `32967846541`, and LEAN clean-determinism `32967846485`.

## Aggregate-safe private runner progress

Luna reported that the local private scorer package exists under the authorized private runner workspace. The synthetic scorer suite passed 25 tests, WSL2 CLI startup passed, and deterministic packaging produced SHA-256 `385a95ee8d35eb6264b1c67026d4355ba25fe80026eaad11fed68055a977924f`.

The reported one-shot invocation is:

```text
python -m scorer --candidate staging\candidate --sealed staging\sealed --runtime staging\runtime --output staging\output --candidate-hash ed2b7b335f4be0f256fc7b28b8df12ae0a337c7b2bdec0c9925ddcd9bef630ff
```

No real sealed corpus was executed and no seal use was consumed. No hidden cases, labels, case IDs, expected outputs, traces, oracle internals, or hidden counts were exported to the public repository.

Synthetic success is runner-mechanics evidence only and does not satisfy `HIDDEN_ACCEPTANCE`.

## Remaining blocker

The remaining execution prerequisites are the registered private evaluator, authorized sealed A1 bundle, pinned LEAN runtime, and a locked-down scorer launch with no credentials/general network and read-only candidate/sealed/runtime inputs. Only the output boundary may be writable.

## Next exact action

1. Freeze the scorer package at the reported SHA-256 and do not modify it after staging without creating a new package hash.
2. Stage the authorized sealed A1 bundle, pinned LEAN runtime, and registered private evaluator into the isolated scorer environment.
3. Before any real seal use, revalidate the frozen public evaluation SHA, candidate artifact SHA-256, scorer package SHA-256, LEAN pin, seal commitment/use budget, synthetic suite, public preflight, credential absence, network isolation, and read-only input mounts.
4. Execute exactly one authorized sealed A1 run.
5. Export only the permitted public `SealRecord`, aggregate-only `SafeAcceptanceReceipt`, candidate artifact SHA-256, and aggregate verifier status.
6. Verify the aggregate evidence fail-closed in the public verifier/workflow. Do not inspect hidden details or consume another seal use as an iterative debugger.
7. Only after every A1 gate is green may issue #15 assign runtime dispositions or select a primary runtime. Issue #16 remains blocked.
