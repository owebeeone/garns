# W1A11-ContractAmendment — CODE-AXIS REVIEW

**Review object:** `W1A11-ContractAmendment` after architectural remediation 1, at 59-file filesystem manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`; controlling `dev-docs/W1A11-ContractAmendment.md` SHA-256 `21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b`; builder-complete candidate, not accepted, 2026-10-04.  
**Baseline:** Approved no-Git filesystem exception. Current sources were read from the verified live tuple, remediation changes were compared with the preserved Revision1 47-file manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`, and controlling historical sources were read from the immutable 120-file baseline archive manifest SHA-256 `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf`.  
**Date:** 2026-10-04  
**Axis:** Code — architecture, interfaces, call graphs, and compatibility reality. Attack: interface contracts versus actual call sites; ownership and visibility; compatibility; error paths; and whether the diff implements its controlling documents without forbidden executable seams. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three P2 findings block. I pre-commit to GO on a revision that resolves P2-1 through P2-3 as specified.

---

## 0. Evidence base

I read the canonical Code prompt in full and verified SHA-256 `25b32e6656daca7475a743f8d8ab9cd79931f86a5464de1c62d54cf9c50427cd`; the workspace and repository instructions; the review-loop skill and canonical template; parent-plan §§15–16; the complete execution brief, ownership extension, amendment, original and remediation DRAFTs, remediation plan and inputs, prior 18 blocking findings and manager counterexamples, verification testimony, PRODUCT_LAYOUT, W1/W2 acceptances, all A1–A16 ADRs, both accepted W2 designs, and the complete current contract/reference/test sources. I did not read any current-round peer/origin report or prompt.

At both start and end:

- The 59-file current manifest verified 59/59, with manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`.
- Inputs verified 9/9, Control 3/3, Baseline 120/120, ReadOnly 111/111, ProductGuard 614/614, and RemInputs 13/13, all with zero failures and their pinned hashes.
- The preserved Revision1 manifest verified 47/47 from inside its archive and retained SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`.
- The seven historical nested manifests verified from inside the baseline archive: 26, 11, 18, 5, 13, 13, and 48 entries respectively.

The authorized Python 3.14 focused command passed 85/85 tests, and `tools/check_product.py` passed all five checks. No full suite was run because it was not an authorized reviewer command. Bytecode was disabled; no files, generated evidence, Git state, services, dependencies, or databases were modified.

### Changed-range analysis against Revision1

I inspected every changed hunk in the fourteen modified Revision1 files and the complete three new implementation modules:

- `admission.py`, `protocols.py`, `consumers.py`, `lifetime_reference.py`, and their tests replace raw-plan callables, duplicate parameters, open operation kinds, and unsequenced steps. This is the architectural R1–R3/R7 interface range. Pinned parameters, narrowed kinds, and ordinary sequential ordering are present, but P2-1 shows the callback boundary and step transaction are still not closed.
- `buffer_reference.py`, `lifetime.py`, `lifetime_reference.py`, and lifetime tests add R5/R11 registration and permit ownership. Exact cross-handle/copy/replay attacks are now rejected, but P2-2 shows that the new scalar registration cursor cannot represent more than one accepted queued envelope.
- `generation_reference.py`, `recovery.py`, and generation tests add sealed permits, activation proofs, migration recovery, and admission epochs. Permit issuance, migration recovery, and epoch invalidation hold; P2-3 shows unused withdrawal is not causally tied to the activation’s physical fence.
- `worker_authority.py` and its tests bind command, worker, authorization, original context, capability, generation, and effect ordinals. The prior unrecorded-command and QUERY-for-mutation paths are closed.
- A16, the amendment, DRAFT-2, remediation plan, exports, and amended tests describe those same changes. No unowned product path changed.

The three findings are incomplete closure of prior roots, not newly discovered architectural roots. P2-1 remains architectural because removing the ordinary callback executable seam changes the corrected consumer interface. P2-2 and P2-3 are bounded corrections within the chosen buffer and activation models. Thus correction 2 would consume the one remaining architectural correction allowance; there is not a third new architectural root in this review.

## 1. Findings

### [P2-1] The closed-consumer abstraction still invokes an ordinary callback inside the raw-plan, uncommitted-step boundary

**Location:** `src/garns/backends/contracts/consumers.py:71-96,104-129`; `src/garns/backends/contracts/lifetime_reference.py:215-248`.

`ReferenceConsumerIssuer.issue` accepts any callable as `effect`. `consume` holds the raw `Plan` in its frame and invokes that callable before returning. `run_plan_step` likewise calls the consumer before committing `last_step_rank`.

Two independent probes demonstrate consequences of this one invocation boundary:

1. An effect raised a caller-defined exception. The caller walked its normal Python traceback and found the `consume` frame’s `plan` local; the recovered value was the exact registry-private plan. Output was `TRACEBACK_PLAN_ESCAPE 1 True`.
2. A `LOWER` effect re-entered `run_plan_step` for `FETCH`. The inner call committed the higher rank, then the outer call overwrote `last_step_rank` with the lower rank. A later ordinary `FETCH` therefore ran again. Output was `REENTRANT_RANK_ROLLBACK ['lower', 'fetch', 'fetch']`. Re-entering the same step likewise ran two effects.

This violates the amendment’s claim that ordinary callbacks never see `Plan`, the R1 lexical-containment requirement, and R3’s strict single operation-step grammar. It permits raw-plan retention and duplicate adapter/lowering effects under one lease despite the new sequential tests passing.

Remove the caller-supplied effect callback from the plan-bearing transaction. The trusted path can construct and return `ClosedStepProduct` after atomically committing the step; test code can inspect that returned closed value outside the private frame. If any callback remains, it must be an issuer-owned non-caller capability, execute only after an irreversible rank reservation, and have no traceback/call-stack path to a frame retaining the plan or admission record.

Closure tests must:

- make a consumer attempt traceback, frame, closure, global, wrapper, and exception-based recovery and prove no raw plan is reachable;
- recursively request the same and a later step while the first step is executing and prove zero duplicate effects and no rank rollback;
- prove an exception leaves the lease contained without making the attempted step retryable.

### [P2-2] One mutable registration cursor makes an earlier accepted queued envelope permanently non-dequeueable

**Location:** `src/garns/backends/contracts/buffer_reference.py:122-173,175-238`; `src/garns/backends/contracts/lifetime_reference.py:398-469`.

`commit_publish` accepts an envelope, marks it queued, and immediately overwrites the registration’s single `cursor` and `last_advancement`. `validate_dequeue` later requires those latest registration values to equal the envelope being dequeued.

A probe registered at cursor 0, published valid envelopes `(0,1]` and `(1,2]`, then attempted normal dequeue of the first envelope. Both publications succeeded and the coordinator count became 2. The first dequeue refused with `refetch_required` while the count remained 2. The second envelope could be dequeued, but the first remained queued and charged; the count still remained 2 because ownership had merely changed from the second buffer to its handoff lease.

This state has no legal normal resolution. If the queue supports capacity at least two, the earlier accepted envelope must remain deliverable in cursor order. If the queue coalesces or has capacity one, accepting the second must atomically invalidate/release or replace the first. The current model instead leaves a valid queued record that its own provenance check can never accept, blocking close or migration until destructive invalidation.

Separate the refresh frontier from per-envelope delivery lineage. Each queued record must retain its immutable enqueue-time registration/cursor relation, and the queue must enforce one explicit outcome: ordered dequeue, atomic coalescing/replacement with exactly-once permit release, or overflow/refetch. Do not compare every queued envelope with only the newest registration cursor.

Closure tests must enqueue at least two sequential ranges and show either:

- both dequeue and complete in order with exact count conservation; or
- documented coalescing/overflow invalidates and releases superseded permits exactly once.

They must also attack later-before-earlier dequeue, duplicate completion, close, and migration barrier installation with the same two-envelope state.

### [P2-3] Unused activation withdrawal accepts a different physical fence from the one that established activation

**Location:** `src/garns/backends/contracts/generation_reference.py:44-77,111-123,268-294`; `src/garns/backends/contracts/recovery.py:46-69`.

`finish_activation` validates `ActivationEvidence` but retains only the protocol epoch and attempted binding. It discards the successful evidence’s `physical_fence_digest`. `withdraw_unused` therefore compares only deployment, binding, and epoch even though `ActivationUnusedWithdrawalProof` contains a physical-fence digest.

A probe finished activation with physical fence `physical-A`, then supplied an otherwise matching withdrawal proof naming `physical-B`. The coordinator accepted it and changed from `ACTIVE_UNUSED` to `UNACTIVATED`, clearing the epoch: `MISMATCHED_FENCE_WITHDRAWAL unactivated None`.

This is not a demand for deferred real physical-fence proof. It is a missing causal comparison between two already-required reference proof fields. The accepted overlay permits unused withdrawal only under the same physical fence, and R9 explicitly requires fence-bound mismatched evidence to preserve `ACTIVE_UNUSED`. Accepting a different fence permits the reference grammar to authorize restoration of legacy access without continuity from the fence that established the activation record.

Retain the successful activation’s fence identity/digest while `ACTIVE_UNUSED` and require exact equality during withdrawal. A mismatch must refuse without changing activation, epoch, attempted binding, or retained evidence. Clear the retained activation evidence only after a valid withdrawal or irreversible first lifetime open.

The closure test must attempt withdrawal with wrong deployment, binding, epoch, and physical-fence digest independently, snapshot all activation fields before each attempt, and prove each refusal is mutation-free. A matching same-fence withdrawal and irreversible first open must remain successful.

## 2. Invariant analysis

### Prior-finding closure table

“Closed” below means the original counterexample and adjacent paths I attacked hold on this exact tuple; it does not override the overall NO-GO.

| Prior blocking ID | Status on MANIFEST-2 | Independent causal result |
|---|---|---|
| Code P2-1 | **OPEN → current P2-1** | The old direct Plan-taking lambda is gone, but an accepted registered effect recovers the exact private Plan through its propagated traceback. Lexical containment is not closed. |
| Code P2-2 | Closed | Executable protocols no longer take a second parameter set; the closed product is built from the lease’s detached `ParameterValues`. |
| Code P2-3 | **OPEN → current P2-1** | Ordinary sequential duplicate/backward/publication tests refuse, but callback reentrancy runs a later step, lets the outer call roll the rank backward, and permits that later step again. |
| Code P2-4 | Closed | Admissions and leases retain coordinator admission epoch; after no-effect reopen, old admission and old lease refuse while newly admitted work succeeds. |
| Code P2-5 | **OPEN → current P2-2** | Cross-handle, copied, stale, and replay envelope attacks now refuse, but sequential accepted buffers break cursor lineage and retain an undequeueable charged permit. |
| Code P2-6 | Closed | Dispatch stores the exact command/worker/authorization tuple; wrong or unrecorded dequeue/effect attempts produce zero effects. |
| Code P2-7 | Closed | Privileged mutation/migration kinds were removed from the read-operation grammar, and capability lookup is exhaustive for the remaining exact kinds. |
| Code P2-8 | Closed | `close_outcome` from `LOCAL_OPEN` refuses without mutation; installed drain/fence blocks new descendant acquisition and preserves peers. |
| Code P2-9 | **OPEN → current P2-3** | `None`, stale epoch, and mismatched binding proofs now refuse, but withdrawal under a different physical fence is accepted. |
| State P2-1 | Closed | Generation permits are sealed exact identities held in private coordinator records; forged, wrong-owner, cross-coordinator, and replay releases preserve counts. |
| State P2-2 | Closed | Close invalidates selected queued buffers once, releases their permits, retains active handoffs, and does not consume peer buffers. |
| State P2-3 | **OPEN → current P2-2** | Exact-envelope mismatch attacks close, but the authoritative cursor/advancement lineage cannot represent two accepted queued envelopes. |
| State P2-4, including expanded revocation vector | Closed | Publication is single-use, requires prior running work, and revalidates authority, admission/registry/coordinator epochs, binding, permit, and local fences. Refresh enqueue uses its guarded barrier. Revocation/expiry/fence probes produce no publication. The separate non-publication reentrancy defect is current P2-1. |
| State P2-5 | **OPEN → current P2-3** | Typed activation proofs and irreversible `ACTIVE` exist, but unused withdrawal does not compare the required same-fence identity. |
| State P2-6 | Closed | `MIGRATION_INDETERMINATE` has exact proof-bearing next-success, full-rollback/new-epoch, and binding-non-reuse exits; mismatched proofs refuse. |
| State P2-7 | Closed | Operation capability is registry-derived from a closed map, and the read grammar no longer exposes mutation or migration leases. |
| State P2-8 | Closed | Parameters are pinned once at acquisition and are not independently supplied to execute/snapshot/subscribe. |
| State-Supp-P2-1 | Closed | Owner/state legality is validated before mutation; rejected queued transfer preserves the old owner, state, completion, charges, and count. |

Other attacked invariants held:

- Result roles are closed and lossless; reserved structural aliases refuse; nested-owner type, cardinality, and one-to-one linkage satisfy all five normative vectors while legacy visible fields retain their default role.
- Handles, leases, generation permits, buffer permits, registrations, consumers, and worker authorizations are sealed exact identities and reject copying/serialization or cross-issuer use.
- Raw `Plan` has been removed from executable backend protocol signatures, there is no legacy `plan_admission_v1` fallback, and fixture admission is named separately from production-shaped rebuilt-plan comparison.
- Local ancestry charging, peer isolation, hard-fence containment, operation-versus-transaction close knowledge, terminal completion idempotency/conflict, and two-participant global generation counting hold for the attacked schedules.
- Public `TrustedContext` remains issuing-task-bound. Worker authorization privately binds the original live record, command, worker, lease, operation, generation, capability, and one-shot ordinals; expiry, invalidation, wrong tuple, replay, and revocation refuse before effects.
- Migration ordering requires zero permits before effects, no-effect reopen changes admission epoch, old admissions are not relabeled, and the three proof-bearing indeterminate outcomes retain the active protocol epoch.

Those successes do not close the three findings. The focused suite is green because it does not exercise exception-traceback escape, callback reentrancy, two simultaneously queued sequential envelopes, or a same-epoch withdrawal with a mismatched physical-fence digest.

## 3. Risks and next action

Actual resolver provenance, static whole-program flow proof, production async/thread/backend/database coordination, cross-process locking, crash/restart durability, physical fencing, credentials, activation tooling, public naming, and W3 Surface remain legitimately deferred and are not findings. The inherited W1 P3 wrong-method diagnostic also remains the explicitly accepted W3 follow-up.

The single next action is consolidated correction 2:

1. eliminate the ordinary callback from the raw-plan/uncommitted-step boundary and add traceback/reentrancy attacks;
2. give queued envelopes a closed cursor/order/coalescing lifecycle with exact permit conservation;
3. retain and compare the activation fence across `ACTIVE_UNUSED` withdrawal.

P2-1 is an architectural interface correction and therefore uses the remaining architecture allowance. P2-2 and P2-3 are bounded within that correction. Freeze a new exact tuple and obtain fresh peer-blind Code and State review; green aggregate tests or builder testimony alone are not closure.

