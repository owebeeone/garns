# W1A11-ContractAmendment — STATE-AXIS REVIEW

**Review object:** W1A11-ContractAmendment remediation-1 candidate at the exact 59-file filesystem manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`; controlling `dev-docs/W1A11-ContractAmendment.md` SHA-256 `21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b`; not accepted; 2026-10-04.  
**Baseline:** Approved no-Git exact-tuple exception. Corrected sources were read directly from the verified filesystem tuple and compared with the exact archived Revision1 47-file snapshot under `dev-docs/W1A11-ContractAmendment-Revision1/`, manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`, and the immutable accepted 120-file baseline manifest SHA-256 `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf`.  
**Date:** 2026-10-04  
**Axis:** State — durable-state semantics and adversity: state machines, restart legality, ordering, races, recovery grammar and fail-closed direction. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — six P2 findings block. P2-1 through P2-4 are new architectural roots; P2-5 is a bounded validation root; P2-6 is a bounded incomplete publication-barrier correction that leaves prior State P2-4 open. The remaining permitted architectural correction round would be consumed by a consolidated correction of P2-1 through P2-4.

---

## Prior-finding closure table

| Prior ID | Original counterexample retraced on corrected tree | Status |
|---|---|---|
| Code P2-1 | Ordinary callables, forged consumers and cross-issuer consumers refuse before plan access; the exact issuer-owned consumer returns only `ClosedStepProduct`. | Closed |
| Code P2-2 | Parameters are pinned in `_LeaseRecord`; executable protocol signatures no longer accept a second parameter set, and products contain the pinned detached values. | Closed |
| Code P2-3 | Direct `ACQUIRED -> PUBLICATION`, duplicate publication, backward steps and illegal operation-kind steps now refuse. P2-6 below is a distinct in-barrier fence interleaving, not the original direct/repeated-step sequence. | Closed for the original counterexample |
| Code P2-4 | After no-effect reopen, old admissions and old leases fail coordinator-epoch validation; newly admitted work succeeds while the retained old lease stays charged until completion. | Closed |
| Code P2-5 | Cross-handle, copied, stale-parameter and wrong-cursor buffer attacks refuse without changing permit counts. P2-1 below is a separate multi-envelope ordering defect. | Closed |
| Code P2-6 | Dispatch stores the exact command, worker and authorization; dequeue and effect use require that exact tuple. | Closed |
| Code P2-7 | `GOVERNED_MUTATION` and `MIGRATION` were removed from the read-operation grammar; the remaining exact kind-to-capability map is QUERY/LIVE only. | Closed |
| Code P2-8 | `close_outcome` from `LOCAL_OPEN` refuses without mutation, and acquisition through a draining/fenced ancestry refuses. | Closed |
| Code P2-9 | Activation no-effect recovery and unused withdrawal require exact typed binding/epoch proof objects; `None`, stale and mismatched proofs preserve state. | Closed |
| State P2-1 | Generation and buffer permits are sealed exact identities with issuer-private owner records; forged, cross-coordinator, wrong-owner and replay releases preserve counts. | Closed |
| State P2-2 | Local close finds selected queued buffers, invalidates and releases them once, retains peer buffers, and waits for active handoff leases before `CLOSED`. | Closed |
| State P2-3 | The original cross-plan, stale, copied and already-delivered envelope attacks refuse without count mutation. P2-1 below exposes a different queue-lineage defect. | Closed |
| State P2-4, including the supplemental revocation vector | Direct/duplicate publication, expiry, revocation, epoch change and a fence installed before publication now refuse and contain the lease. A fence installed reentrantly during the purported publication linearization point still permits publication; see P2-6. | **Open** |
| State P2-5 | `ACTIVATION_INDETERMINATE` and `ACTIVE_UNUSED` cannot exit on absent, incomplete, stale or mismatched evidence; attempted epochs remain unavailable for reuse. | Closed |
| State P2-6 | `MIGRATION_INDETERMINATE` has proof-bearing requested-next, full-rollback/new-epoch and binding-non-reuse exits; mismatched proof preserves the state. | Closed |
| State P2-7 | Privileged operation kinds no longer enter read admission, and worker capability is derived from the registry-owned operation kind. | Closed |
| State P2-8 | Pinned detached parameters are the only parameters supplied to closed consumers; executable seams have no replacement parameter input. | Closed |
| State-Supp-P2-1 | Illegal owner transfers validate before mutation; the original owner remains usable, the proposed owner remains rejected, and state/counts remain unchanged. | Closed |

## Changed-range analysis

Every changed range against archived Revision1 was inspected.

- `A16-admission-lifetime.md` and `W1A11-ContractAmendment.md` document the remediation’s consumer, provenance, recovery and exact-permit changes. Their publication, queue and whole-operation claims are stronger than the current reference transitions because of P2-1 through P2-4 and P2-6.
- `admission.py` removes privileged read-operation kinds and adds exact capability and step maps. Its independent `NESTED_FETCH`/`TOTAL_FETCH` operations and monotonic-but-not-causal step grammar create P2-3 and P2-4.
- `generation_reference.py` correctly replaces value permits and evidence-free recovery, but does not causally require participant queue barriers and accepts non-successor generations, producing P2-2 and P2-5.
- `lifetime.py` adds sealed generation/buffer identities and closed local transitions; those changes held under attack.
- `lifetime_reference.py` implements the principal remediation state graph. Exact provenance, local buffer invalidation, epoch binding, worker dequeue and rejected-transfer fixes held. Its queue exchange, snapshot publication, migration barrier and publication-callback ordering produce P2-1 through P2-4 and P2-6.
- `model.py` and `protocols.py` correctly export the new values and remove duplicate execution parameters/raw-plan seams.
- `worker_authority.py` correctly binds dispatch to an exact command/worker/authorization tuple and consumes effect ordinals before callbacks.
- New `consumers.py` closes the raw-plan boundary, but its synchronous effect callback exposes the in-barrier reentrancy used by P2-6.
- New `buffer_reference.py` closes the original provenance holes but conflates producer advancement with delivery ordering, producing P2-1.
- New `recovery.py` supplies closed typed activation/migration proof-input shapes; the proof-shape attacks held.
- The changed admission, lifetime, generation, worker and compatibility tests close the listed original counterexamples. They omit multi-envelope FIFO, out-of-phase/skipped migration barriers, snapshot publication without a snapshot product, standalone child/total operations, generation skips and fence reentrancy.

## 0. Evidence base

I read the complete canonical State prompt at SHA-256 `88ae56dcae148cc4360c8890e44a09594537ac10f9989204a22ab6d8b91553c8`, `../AGENTS_GWZ.md`, `AGENTS.md`, the complete review-loop skill and canonical template, and implementation-plan §§15–16.

I read all 59 manifest entries, including A1–A16, every contract module, all seven contract-test files, the execution brief, ownership extension, amendment, initial and remediation DRAFTs, complete remediation plan and inputs, all three legitimate prior State/Code reports, manager counterexamples and verification records. I also read `PRODUCT_LAYOUT.md`, W1 acceptance, the complete accepted W2 base and lifetime overlay, and W2 acceptance. No current-round peer/origin report or prompt was read.

I diffed all fourteen modified files against archived Revision1 and inspected the three new modules. Revision1 verified 47/47 from inside its archive. The seven historical nested manifests verified with exact counts 26/11/18/5/13/13/48 and zero failures.

At both start and end:

- current MANIFEST-2 hash was `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`, 59/59 entries;
- Inputs verified 9/9, Control 3/3, Baseline 120/120, ReadOnly 111/111, ProductGuard 614/614 and RemInputs 13/13;
- amendment, DRAFT-2 and RemPlan retained their pinned hashes;
- no `__pycache__` directory or `.pyc` file was present.

The allowed Python 3.14 focused suite passed 85/85, and `tools/check_product.py` passed 5/5. Green tests did not determine the verdict.

Inline `-B` probes with bytecode disabled reproduced:

```text
count_after_two 2
oldest_dequeue refused ContractRefusal RefusalCode.REFETCH_REQUIRED count 2
newest_dequeue accepted count 2
after_newest_complete_count 1

before_out_of_phase_barrier CURRENT 1 OPEN
after_out_of_phase_barrier 1 CURRENT 0 MIGRATION_INVALIDATING

reopen_without_barrier CURRENT admission_epoch=2 count=1 queue=OPEN
stranded_old_buffer refused ADMISSION_REVOKED count=1

registration_without_snapshot publications=1 count=0

standalone_nested_published publications=1 count=0

generation_skip CURRENT generation=3 admission_epoch=2

reentrant_publication ['publication'] publications=1
lease=CONTAINED resource=LOCAL_FENCED count=1
```

## 1. Findings

### [P2-1] Producer advancement is incorrectly used as the dequeue cursor, making the oldest queued delivery undeliverable

**Location:** `src/garns/backends/contracts/buffer_reference.py:203-210,212-251`; `src/garns/backends/contracts/lifetime_reference.py:450-469`.

`commit_publish` advances the registration’s single `cursor` to each newly queued envelope’s `observed_through`. `validate_dequeue` then requires that same latest cursor to equal the envelope being dequeued. With two legal queued envelopes, the second enqueue changes the cursor from revision 1 to revision 2. The oldest envelope then refuses because its `observed_through` is 1, while the newest envelope can be dequeued first. After completing the newest handoff, the oldest buffer permit remains charged and has no ordinary successful dequeue path.

This violates A6’s ordered cursor lineage and W2 overlay §9’s exact buffer handoff and single-release rules. The impact is skipped/out-of-order delivery, a stranded permit that blocks migration, and forced close/refetch despite a valid bounded queue.

This is a **new architectural root**: producer progress, delivery progress and queue order need distinct issuer-private state. Track a queue sequence/head and separate produced-through versus delivered-through lineage. Dequeue must accept only the exact head whose `previous` matches the delivered cursor; attempting a later envelope must refuse without mutation.

Closure test: enqueue revisions 1 and 2. Dequeue of revision 2 before revision 1 must refuse with both permits intact. Revision 1 then revision 2 must each exchange exactly one buffer permit for one handoff lease, preserve cursor continuity, and leave count zero after terminal completion. Repeat with invalidation between the two envelopes and with copied/cross-registration envelopes.

### [P2-2] Migration queue barriers are not causally coupled to drain, zero, migration or reopen

**Location:** `src/garns/backends/contracts/lifetime_reference.py:521-531`; `src/garns/backends/contracts/generation_reference.py:189-215`.

`migration_queue_barrier` has no coordinator-state or drain-attempt check. It can run while the deployment is ordinary `CURRENT`, discard valid deliveries, release their permits and leave queues `MIGRATION_INVALIDATING` without any migration. Conversely, `reopen_no_effect` requires only `DRAINING_OLD` and “effect not begun”; it does not require that each participant installed and completed its queue barrier. Beginning drain and immediately reopening with an existing buffer leaves the deployment `CURRENT` at a new admission epoch, the queue `OPEN`, and the old buffer permit charged. The old admission can no longer dequeue it, so the buffer is stranded.

The same missing causal link allows `begin_migration` after global count zero without proof that every participant installed the required pre-zero marker. This violates W2 overlay §8.2’s unique authoritative barrier ordering and the prompt’s pre-zero/two-participant requirement. It permits out-of-phase delivery loss and creates a closed-grammar stuck state.

This is a **new architectural root** in the coordinator/participant boundary. A migration attempt needs an exact private identity registered with every participant. Queue invalidation must be legal exactly once in `DRAINING_OLD` for that attempt, and migration or no-effect reopen must require all participant barrier acknowledgements. Reopen must never make an unbarriered old envelope unreachable.

Closure tests must show:

1. a barrier in `CURRENT`, `MIGRATING`, or after reopen refuses without changing queues, buffers or counts;
2. reopen and `begin_migration` refuse until every participant acknowledges the exact current drain attempt;
3. queued buffers are released exactly once;
4. a dequeue winner remains an active lease;
5. skipped, duplicated, stale-attempt and cross-participant acknowledgements cannot advance the coordinator.

### [P2-3] Snapshot registration and refresh candidates are not causally tied to snapshot results produced by their lease

**Location:** `src/garns/backends/contracts/admission.py:112-123,147-155`; `src/garns/backends/contracts/lifetime_reference.py:370-448`; `src/garns/backends/contracts/consumers.py:104-129`.

The step grammar is merely monotonic. A `SNAPSHOT_REGISTRATION` lease may run `REGISTRATION` as its first step, without a fetch, snapshot watermark, rows or assembly. `register_subscription` then accepts an arbitrary caller-supplied cursor and publishes a durable registration. The probe registered revision 999 and incremented `publications` without producing a snapshot candidate.

The refresh path has the same structural gap: a guarded step product contains plan metadata and parameters but no rows, watermark or advancement identity. `create_refresh_candidate` accepts caller-supplied rows and cursors after any earlier legal step. Exact admission/binding/parameter comparison therefore does not establish that the buffered rows and high-water cursor came from the leased snapshot.

This violates W2 overlay §§5 and 9: `(rows,S,registration)` and `(rows,H)` must be produced and published under the same exact lease, and an arbitrary cursor cannot silently skip durable revisions. This is not a demand for real database evidence; it is a missing internal causal contract.

This is a **new architectural root**. Introduce sealed issuer-private snapshot/refresh candidate identities containing the operation, rows, watermark, cursor lineage and advancement produced by the guarded step. Registration and buffer publication must consume the exact candidate once at the publication barrier.

Closure tests: direct registration after `REGISTRATION` alone, fabricated cursor/rows, cross-lease candidate, repeated candidate, stale candidate and candidate after authority/fence change must all yield zero publication and unchanged counts. A valid initial snapshot must atomically publish its rows, cursor and registration, and a valid refresh must publish only its exact candidate.

### [P2-4] Nested and total fetches are independent leases with no parent-operation relationship

**Location:** `src/garns/backends/contracts/admission.py:50-57,128-137`; `src/garns/backends/contracts/lifetime_reference.py:55-74,77-84,159-213`.

`NESTED_FETCH` and `TOTAL_FETCH` are independently acquirable query operation kinds. `_LeaseRecord` has no parent lease or operation field. A query handle can therefore acquire a standalone nested-fetch lease, run `LOWER`, `CHILD_FETCH` and `PUBLICATION`, then succeed with no parent execution. The probe produced one publication and returned the generation count to zero.

The accepted overlay explicitly requires child/nested/total work to remain within the parent lease and forbids a derived primitive from outliving it. Independent permits let child work survive parent completion or containment and make parent close/cancellation incapable of expressing the whole operation.

This is a **new architectural root**. Remove independent public acquisition for nested/total kinds and model each child/total command under the parent lease’s exact operation, owner and permit. If subordinate identities are needed, they must be issuer-private children whose terminal state cannot outlive or publish independently of the parent.

Closure test: direct acquisition of nested/total work must refuse without a permit. Multiple child and total commands must execute under one parent lease, remain charged through the parent, become contained when the parent is fenced, and be unable to publish or complete after the parent’s terminal outcome.

### [P2-5] The generation coordinator permits migration to skip generations

**Location:** `src/garns/backends/contracts/generation_reference.py:206-231`; controlling successor rule at `src/garns/backends/contracts/operations.py:105-110`.

`begin_migration` accepts any requested generation greater than the old generation. Starting from generation 1, a request for generation 3 reaches `MIGRATING`, begins effects and publishes `CURRENT` generation 3. The accepted A12 request contract requires exactly `after.generation == before.generation + 1`, and “requested next binding” cannot mean an arbitrary greater generation.

This is a **bounded new root**. Require the requested binding to be the exact successor of the pinned old binding and keep that exact request through effect, publication and recovery.

Closure test: generations equal to, below, or more than one above the old generation must refuse before state/effect mutation; only `old + 1` may become `_requested_binding`. Apply the same exact-successor validation to migration recovery proofs.

### [P2-6] The publication callback runs before publication commitment and can install a hard fence that the method then crosses

**Location:** `src/garns/backends/contracts/lifetime_reference.py:215-248`; `src/garns/backends/contracts/consumers.py:104-129`.

`run_plan_step` validates barriers, changes the lease to `PUBLISHING`, then invokes the registered consumer effect. Only after the callback returns does it set `publication_committed` and increment `publications`. A deterministic callback that calls `start_close(connection, hard=True)` changes the lease to `CONTAINED` and the resource to `LOCAL_FENCED`. On return, `run_plan_step` nevertheless records publication and returns the product:

```text
effect=['publication']
publications=1
lease=CONTAINED
resource=LOCAL_FENCED
count=1
```

The supposed linearization point therefore permits visibility after its own lease and ancestry were fenced. This leaves prior State P2-4/R3 incompletely corrected.

This is a **bounded correction within the accepted publication-barrier architecture**. Pure consumer work must finish before the atomic visibility transition, followed by a final barrier validation and compare-and-transition from the still-owned expected state; alternatively, commit visibility before invoking any outward observer. A callback must not be able to mutate the lease/resource mid-barrier and have publication committed afterward.

Closure test: reentrantly invoke graceful drain, hard fence, generation revocation, epoch change and conflicting completion from the consumer callback. Every mutation that wins before publication commitment must result in zero publication and retained containment; a publication that wins must be durably committed before any observer runs and must not later be relabeled as unpublished.

## 2. Invariant analysis

Attacks that held:

- Admission, lease, generation, buffer, consumer, registration and worker handles are sealed exact identities and reject ordinary construction, copying and serialization.
- Original raw-plan escape, duplicate parameter and privileged read-kind paths are removed.
- Original direct, duplicate, backward and post-publication step attacks refuse.
- Original revoked/expired/pre-fenced publication attempts contain the lease and do not increment publication.
- Generation reopen invalidates old handles and leases through the coordinator epoch.
- Exact permit ownership prevents forged, equal-value, cross-coordinator and replay release.
- Local close invalidates selected queued buffers once, retains peer buffers and waits for dequeued handoffs.
- Worker dispatch/dequeue/effect checks exact command, worker, authorization, runtime, binding and ordinal; expiry, invalidation and revocation produce zero effects.
- Activation remains one-time; absent/stale negative evidence cannot resolve indeterminate or unused activation; `ACTIVE` has no reset/deactivation edge.
- All three migration-indeterminate proof kinds exist, reject mismatched epochs and preserve the active protocol epoch.
- Rejected owner transfer preserves state, owner and count.
- Exact identical terminal completion is idempotent and conflicting completion refuses.

Those successes do not repair the new roots. The reference model still cannot represent an ordered multi-envelope delivery queue, cannot prove its queue barrier occurred in the required migration attempt, cannot tie snapshot rows/watermark to registration, and exposes child/total work as independent operations. Its publication ordering also allows a fence to win inside the barrier and then be ignored.

The passing deterministic suite proves only the schedules it contains. No claim is made here about deferred production planners, threads, locks, databases, physical activation fencing, crash recovery or cross-process coordination.

## 3. Risks and next action

Deferred production and restart evidence remains a legitimate residual risk, not a finding. No P3-only issue is filed.

The single next action is one consolidated architecture remediation 2 covering P2-1 through P2-6, with distinct producer/delivery cursor state, migration-attempt barrier acknowledgements, sealed snapshot/refresh candidates, parent-owned child/total work, exact successor validation and a genuinely atomic publication transition. Because P2-1 through P2-4 change shared state/interface architecture, the corrected tuple requires fresh full peer-blind Code/State review. If another architectural root is found after that correction, the two-round cap requires stopping the lane for operator redesign-or-accept rather than another patch.

