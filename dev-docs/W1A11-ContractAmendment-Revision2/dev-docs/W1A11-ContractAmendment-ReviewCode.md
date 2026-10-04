# W1A11-ContractAmendment — CODE-AXIS REVIEW

**Review object:** W1A11-ContractAmendment at 47-file filesystem manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`; controlling `dev-docs/W1A11-ContractAmendment.md` SHA-256 `e5293ebeb777a31f07203bcba6860e5875fb0d1e643ea98f3a49efc92438db48`; builder-complete candidate, not accepted, 2026-10-04.  
**Baseline:** approved no-Git filesystem exception. Sources were read from the live tree and compared with the 120-file archived accepted source at `dev-docs/W1A11-ContractAmendment-Baseline/`, manifest SHA-256 `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf`. Inputs, read-only and product guards were read and verified recursively.  
**Date:** 2026-10-04  
**Axis:** Code — architecture, interfaces, call graphs, ownership, compatibility and executable-contract reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — nine P2 findings block.

---

## 0. Evidence base

I read the canonical Code prompt in full and verified its SHA-256 `286729524b6d994000d9c96605e410bcf49abe0d332e8368f2f810b4f31b97e9`; `AGENTS_GWZ.md`, `AGENTS.md`, the review-loop skill/template, current checkpoint, plan §§15–16, execution brief, ownership extension, amendment/DRAFT, A1–A16, PRODUCT_LAYOUT, W1/W2 acceptances, and both accepted W2 documents in full.

I inspected and diffed every amended contract file against the archive, with detailed line review of `semantic.py`, `protocols.py`, `admission.py`, `lifetime.py`, `lifetime_reference.py`, `generation_reference.py`, `worker_authority.py`, `authority.py`, `state.py`, `values.py`, exports, and all six contract-test files.

At start and end, all 47 current entries, 9 inputs, control entries, 120 baseline entries, 111 read-only entries and 614 product-guard entries verified. All seven historical nested manifests verified from inside the archive. The focused suite passed 76/76 and `tools/check_product.py` passed 5/5.

Inline `-B` probes reproduced every finding below. These included raw-plan caching/property escape, parameter substitution, duplicate/out-of-order publication, old-handle reuse after admission-epoch change, forged-buffer relabeling, unbound worker-command effects, query-authorized mutation/migration, and close without drain.

## 1. Findings

### [P2-1] The lexical plan guard hands raw plans to arbitrary callables that can retain them

`admission.py:190-196` exposes `Callable[[Plan], …]`; `lifetime_reference.py:218-245,478-505` checks only the returned object after the callable has executed. A continuation `lambda plan: cache.append(plan) or "command"` succeeds and leaves the private plan in caller storage. A zero-slot object whose property returns the plan also passes `_contains_plan`. This violates A16 lines 8–16 and the no-plan/cache/closure boundary. Replace arbitrary continuations with issuer-owned registered exact consumers and closed output types; do not expose `Plan` through a caller-supplied callable. Regression tests must attempt side-effect caching, property/descriptors, globals, wrappers and closures. Classification: architectural.

### [P2-2] Lease acquisition and executable protocols carry two independent parameter sets

`_LeaseRecord.parameters` pins acquisition parameters at `lifetime_reference.py:68-78,203-213`, but `protocols.py:37-41,78-80` accepts another `ParameterValues`, and `run_plan_step` neither supplies nor compares the pinned value. A lease acquired with `tenant=A` successfully drove an adapter callback closed over `tenant=B`. Admission can therefore validate one input while execution uses another. Remove the duplicate protocol argument or compare it exactly before any callback and expose only the registry-pinned detached values to a closed consumer. Add mismatch tests at execute, snapshot and subscribe with zero callback/effect counts. Classification: architectural.

### [P2-3] Plan-step state has no ordering or one-shot publication grammar

`lifetime_reference.py:218-245` accepts every `PlanStep` in every live nonterminal state. An `ACQUIRED` lease published twice, incremented `publications` twice, then ran `ADAPTER_START` after publication and completed successfully. This contradicts whole-operation ordering and exactly-once public handoff. Track a closed per-operation step grammar and committed-publication bit; reject duplicate, backward and post-publication work before invoking the callback. Test every illegal edge and require unchanged state/counters. Classification: architectural.

### [P2-4] No-effect migration reopen changes coordinator epoch without invalidating admitted handles

`generation_reference.py:138-142` increments `admission_epoch`, but admissions store only the registry epoch (`lifetime_reference.py:51-58,167-172`) and acquisition never compares the coordinator epoch. After `begin_drain`/`reopen_no_effect`, an old handle acquired a new lease at epoch 2 despite being admitted at epoch 1. This violates the accepted rule that old handles remain invalid after reopen. Bind admissions to coordinator admission epoch and revoke/re-admit on reopen. Test old-handle refusal and newly admitted-handle success after a no-effect reopen. Classification: bounded contract correction.

### [P2-5] Buffered-delivery provenance is never linked to the refresh admission or dequeue handle

`lifetime_reference.py:374-422` checks only deployment/generation. It does not compare envelope admission identity, plan digest, registration or cursor lineage with the refresh lease/admission, and dequeue accepts any handle. A buffer with a forged identity and digest was published from one refresh and dequeued under a real unrelated handle. This permits stale/wrong-plan rows to be relabeled. Store subscription-registration provenance, validate every envelope field at the atomic refresh-to-buffer exchange, and require the same admission/registration during dequeue. Add mismatch attacks asserting no buffer/handoff permit and unchanged counts. Classification: architectural.

### [P2-6] Worker command identity is not part of lease ownership

`_LeaseRecord` has no command field; `transfer_owner` accepts only a new owner (`lifetime_reference.py:68-78,247-258`), and `worker_operation_live` ignores its `command` argument (`315-328`). An authorization for an arbitrary command produced an effect after the lease was transferred directly to the worker; nothing tied that command to queue insertion. Add exact command identity and authorization to the atomic queued-owner record and require matching command-to-worker dequeue before effects. Regression must issue authorization for an unrecorded command and observe zero effects. Classification: architectural.

### [P2-7] Privileged operation kinds default to QUERY authority

`lifetime_reference.py:187-192,230-235` maps only live kinds specially and treats every other kind as `Capability.QUERY`. Consequently a QUERY-only context acquired both `GOVERNED_MUTATION` and `MIGRATION` leases and ran adapter callbacks. Either remove these kinds from the read-admission grammar or map every exact kind exhaustively to its required capability. Tests must show query-only callers create no lease/effect for governed mutation or migration. Classification: bounded correctness correction.

### [P2-8] Close finalization can run without first installing the drain barrier

`close_outcome` at `lifetime_reference.py:346-372` does not require `LOCAL_DRAINING` or `LOCAL_FENCED`. With one active lease, direct `close_outcome(runtime)` returned `NONQUIESCENT` while leaving the runtime open, and another acquisition succeeded; with no lease it changed an open runtime directly to closed. Require the close-start state before outcome/finalization and enforce legal local transitions. Test direct finalization from OPEN and new acquisition after a close attempt; both must refuse without mutation. Classification: bounded correctness correction.

### [P2-9] Activation rollback transitions accept no authoritative proof input

`generation_reference.py:64-78` treats `recover_activation(None)` as sufficient to leave `ACTIVATION_INDETERMINATE`; `withdraw_unused` at lines 87–91 accepts only an epoch. The accepted design requires authoritative no-activation/no-ever-open proof plus restored physical access fencing. Real proof is deferred, but its internal shape is not. Add exact recovery/withdrawal evidence values representing inventory, durable-record outcome and physical access restoration; absent/mismatched evidence must preserve indeterminate/unused state. Classification: architectural interface-shape defect.

## 2. Invariant analysis

Several attacks held: result roles are closed, independent key flags survive the five fixtures, nested owners link one-to-one, legacy visible fields retain their default role, handles are empty/sealed/noncopyable, raw `Plan` was removed from executable backend signatures, ordinary ancestry charging and peer-local close isolation work, public contexts remain task-bound, effect ordinals are consumed before callbacks, active protocol reset is refused, and two registries share generation counts.

Those successes do not close the findings: the verifier itself leaks plans, operation inputs are split, transition ordering is unenforced, epoch/provenance/command links are absent, and privileged kinds are under-authorized. Green tests omit the reproduced hostile sequences and in places encode the defect—for example, the fake connection publishes directly from acquisition and worker tests transfer ownership to a worker without ever binding the tested command.

## 3. Risks and next action

Deferred production planner/backend/thread/database evidence remains legitimately unproven and is not a finding. The immediate action is one consolidated correction covering P2-1 through P2-9, with the specified counterexample tests. Because P2-1, P2-2, P2-3, P2-5, P2-6 and P2-9 alter shared interfaces or authority/lifetime architecture, the corrected tuple requires fresh full peer-blind review rather than only focused closure.
