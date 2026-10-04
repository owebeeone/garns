# W1A11-ContractAmendment — STATE-AXIS REVIEW

**Review object:** `dev-docs/W1A11-ContractAmendment.md` at SHA-256 `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`; final architecture correction 2 of 2, builder writes stopped, not accepted. Live filesystem object is `W1A11-ContractAmendment-MANIFEST-3.sha256` at `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`, 71 files.

**Baseline:** Approved no-Git filesystem exception. Current source was compared against archived Revision2 complete59 (`MANIFEST-2` SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`, 59/59 verified), archived Revision1 complete47 (`MANIFEST` SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`, 47/47 verified), and accepted Baseline120.

**Date:** 2026-10-04

**Axis:** Durable-state semantics and adversity: closed state machines, ownership, fail-closed progress, recovery grammar, queue/permit exchanges, migration and activation. Independent, adversarial, read-only. The other axis ran in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three P2 findings block. `P2-1` is a new architectural root in the final correction2 object and triggers the required STOP/operator redesign-or-accept decision. `P2-2` is a bounded residual of F2. `P2-3` is a new bounded omission. I do not pre-commit to GO because the worker-exit lifecycle requires an operator-directed architectural decision.

---

## 0. Evidence base

The exact live tuple was checked at both review boundaries:

- Start: MANIFEST-3 hash matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71 entries; 71/71 verified.
- End: the same manifest hash, 71 entries, and 71/71 verification.
- The review prompt remained at `b3112bae56d1ebf58bf77de56de8ae7b0bd6e21a8b3d5c73c48f1dc48dc6bc8b`.
- DRAFT-3 remained at `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`.
- RemPlan-2 remained at `749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c`.

Controlling manifests verified:

| Manifest | SHA-256 | Result |
|---|---|---:|
| Inputs | `032508b3b5ba210be4b53d939c1301e85a06083b787727a2fd9bf78270b9da24` | 9/9 |
| Control | `3d614336ae2a944fe40fbefa79ca48be662d839ddb1d163abeb7353bccf84951` | 3/3 |
| Baseline | `a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf` | 120/120 |
| ReadOnly | `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` | 111/111 |
| ProductGuard | `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` | 614/614 |
| RemInputs | `6abcd861c58160bec0c2124a0dda680456ff6dcf0e06eff05110d234cb5bae63` | 13/13 |
| RemInputs-2 | `b96517c9cfb8e3f35622242b61a135cbb42b784f5c8b8245081d58e30b4280ac` | 16/16 |

The seven historical manifests were verified from inside the preserved Baseline archive: 26/26, 11/11, 18/18, 5/5, 13/13, 13/13, and 48/48.

I read the complete governing instructions and review template; implementation-plan §§15–16; ExecutionBrief and OwnershipExtension; the accepted W2 query-planning and admission/lifetime designs; W2 and W1 acceptance; PRODUCT_LAYOUT; A1–A16; the amendment and DRAFT-3; RemPlan/RemPlan-2; and every legitimate prior Code, State, supplement, round-2, and origin-closure report. I did not read any prohibited current Code/State-3, Origin/Fresh Closure-2 report or prompt, nor current manager checkpoint/restart findings.

I inspected all current contract source and contract tests, including the two new reference modules, and diffed every declared changed path against Revision2. State-critical inspection included:

- `lifetime_reference.py:189-387,395-423,425-652,718-785`
- `worker_authority.py:90-185`
- `buffer_reference.py:150-314`
- `snapshot_reference.py`
- `migration_reference.py`
- `generation_reference.py`
- `admission.py`, `authority.py`, `consumers.py`, `recovery.py`, `lifetime.py`
- all six `tests/contracts/test_*.py` files.

Allowed execution evidence:

- Python 3.14 focused contract suite: 97/97 passed.
- `tools/check_product.py`: all five checks passed.
- Inline `-B` probes exercised prior counterexamples plus new adverse sequences without filesystem writes.

The important new probe results were:

```text
FIRST_EFFECT RuntimeError:boom
AFTER_EXCEPTION running 1
SECOND_EFFECT_AFTER_EXCEPTION accepted ['second'] running

RETURN_TRANSFER ContractRefusal:lease_owner_conflict running
CALLER_COMPLETION ContractRefusal:lease_owner_conflict running
```

A refused active delivery probe expired its context after `VALIDATE` but before `PUBLICATION`, completed the contained lease as `REFUSED`, and then successfully dequeued the second FIFO range.

A neutral-refresh probe completed a sealed empty refresh candidate without publishing a buffer. The next refresh from the supposedly advanced cursor refused with `REFETCH_REQUIRED`; the only path that did advance the producer cursor created a queued delivery permit.

Passing suites do not close these counterexamples.

## 1. Findings

### [P2-1] The worker lifecycle has no post-dispatch result or failure ownership transition

**Classification:** New architectural root.

**Location:** The accepted lifecycle requires worker-to-runtime result handoff and worker-to-containment transfer as compare-and-transfer operations naming the expected owner (`W2-AdmissionLifetimeRedesign.md:249-257`). It also requires exceptions or cancellation after dispatch to retain containment until authoritative worker quiescence (`:765-769`).

Current implementation:

- `lifetime_reference.py:300-308` permits generic transfer only from `ACQUIRED`; a `RUNNING` worker cannot transfer to the runtime or a containment owner.
- `:310-342` transfers caller → command → worker and stops there.
- `:348-352` changes the state to `CONTAINED` but does not transfer ownership to a containment owner.
- `worker_authority.py:138-180` consumes an effect ordinal and directly invokes `effect()` without installing containment or revoking remaining ordinals if that invocation raises.

**Violated invariant:** Dispatch, result handoff, cancellation, and failure form one closed compare-and-transfer ownership grammar. A begun or failed worker effect may not remain ordinary `RUNNING` work with further authority, and no caller may release or publish a worker-owned lease without an exact return transition.

**Reproduction:** Acquire an `EXECUTE` lease, dispatch a command with effect ordinals `(1, 2)`, make the assigned worker current, and dequeue. Let ordinal 1’s effect raise `RuntimeError`. The lease remains `RUNNING`, the generation count remains one, and ordinal 2 is still accepted and runs. An exact worker-to-caller `transfer_owner` then refuses because the state is not `ACQUIRED`; caller completion also refuses because the worker remains owner.

Even an explicit `contain(lease, worker)` only changes state: it does not establish the separately required containment owner.

**Impact:** A worker effect may fail after beginning yet leave later effects authorized. Successful work also lacks the required result-handoff transition to a runtime owner for guarded publication/completion. The model therefore cannot represent the accepted post-worker lifecycle or prove who owns recovery after an indeterminate effect.

**Required correction:** Operator-directed redesign must define the missing worker-exit half of the protocol: an exact worker-to-runtime result transfer and an exact worker-to-containment failure/cancellation transfer, both bound to the live lease/command/authorization/worker tuple. Effect exceptions must atomically enter containment and revoke all unused ordinals without releasing the permit before authoritative quiescence. The resulting owner must be the only owner able to publish or complete.

**Closure test:** Exercise successful handoff, wrong-worker/wrong-command/wrong-authorization transfer, effect exception, cancellation during an effect, and containment completion. After an effect exception, the lease must already be contained under the exact containment owner, unused ordinals must refuse, counts must remain charged until authoritative resolution, and neither the former worker nor caller may publish or complete. A successful result transfer must allow only the exact new runtime owner to pass the publication barrier.

### [P2-2] A refused active handoff falsely advances delivered progress and skips an unseen FIFO range

**Classification:** Bounded residual of F2 (`Code2 P2-2` / `State2 P2-1`).

**Location:**

- `lifetime_reference.py:360-387` calls `complete_handoff` for every terminal outcome whenever a handoff envelope exists.
- `buffer_reference.py:266-276` always removes the FIFO head and advances `delivered_through`, with no knowledge of outcome or publication commitment.
- `buffer_reference.py:219-247` consequently admits the following range once that false cursor advance occurs.

**Violated invariant:** Delivery progress records caller-visible delivery, not mere dequeue or terminal lease disposal. Failures may lose local progress and force refetch; they may not invent delivery of a batch that never crossed the publication boundary. F2 explicitly required exact produced/delivered/head progress and rejection coverage.

**Reproduction:** Publish ranges `(0,1]` and `(1,2]`. Dequeue the first and complete `VALIDATE`. Expire its context before `PUBLICATION`; barrier validation contains the lease and nothing becomes caller-visible. Complete it as `REFUSED`. Current completion pops the first envelope and writes `delivered_through = 1`. With a renewed context, the second range then dequeues successfully because its `previous == 1`.

**Impact:** The first batch is silently skipped while the state claims it was delivered. This violates A6 ordered delivery and the state-axis fail-closed rule. It can expose later state while permanently hiding an earlier caller-visible transition.

**Required correction:** Make handoff finalization depend on exact publication commitment and terminal outcome. Only a successfully committed caller-visible handoff may advance `delivered_through`. A refused or cancelled pre-publication handoff must conservatively retire/invalidate the registration and queued successors or preserve an explicit retryable head; either rule must return `RefetchRequired` rather than silently skip. Permit and shared-count release must remain exact-once.

**Closure test:** Queue two sequential ranges. For the head, exercise context expiry, authority revocation, local fence, and consumer failure between dequeue and publication, then complete with every legal non-success outcome. Assert no delivered cursor advance, no successor dequeue, no duplicate permit release, and an explicit refetch/retirement result. Retain the existing two-range successful FIFO and idempotent-success tests.

### [P2-3] The required neutral-refresh state transition is absent

**Classification:** New bounded omission.

**Location:** A6 requires neutral refresh to advance the internal cursor without emitting a batch (`docs/adr/A6-subscription-snapshot.md:10-16`). The accepted lifecycle repeats this rule at `W2-AdmissionLifetimeRedesign.md:631-637` and names it as a mandatory closure vector at `:778`.

Current implementation has only two outcomes:

- `lifetime_reference.py:503-540` creates a sealed refresh candidate after checking the current `produced_through`.
- Completing that lease without publication leaves the registration cursor unchanged.
- `lifetime_reference.py:542-589` and `buffer_reference.py:209-217` advance `produced_through` only while creating and committing a queued `BufferedDelivery`.

There is no neutral/no-batch candidate-consumption transition.

**Violated invariant:** A trusted `(rows,H)` refresh that changes no public state must atomically advance the internal cursor under its lease without creating a delivery, while preserving the same generation, authority, queue, and lineage barriers.

**Reproduction:** Register at cursor 0, acquire a refresh, complete FETCH/ASSEMBLY/CURSOR_ADVANCE, and create its sealed candidate through cursor 1 with no changed rows. Completing the lease as `SUCCEEDED` emits no batch but leaves `produced_through` at 0; the next candidate with `previous=1` refuses `REFETCH_REQUIRED`. Calling `publish_refresh_buffer` is the only way to advance, but that creates an envelope and buffered-delivery permit.

**Impact:** The reference contract must either emit a spurious public batch for a neutral refresh or fail to advance and refetch unnecessarily. It does not implement the accepted A6 state grammar.

**Required correction:** Add a sealed, lease-bound neutral result or an explicit trusted neutral classification on the refresh candidate. Its commit must revalidate the same authority, generation, queue, admission, and cursor barriers; consume the candidate once; advance only the internal produced cursor/durable advancement; create no envelope or buffered permit; and release the refresh lease exactly once.

**Closure test:** Commit a trusted neutral candidate from cursor 0 to 1 and assert no envelope, queue entry, delivery permit, or public batch. A following non-neutral refresh from 1 must succeed. Fabricated, copied, stale, cross-lease, cross-registration, fenced, and repeated neutral candidates must refuse without advancing the cursor or changing counts.

## 2. Invariant analysis

### Initial 18-finding closure table

| Initial finding | Result on MANIFEST-3 | Retraced evidence |
|---|---|---|
| Code P2-1 — raw Plan to arbitrary callable | **CLOSED** | Fixed issuer-owned consumers return closed products; raw-plan and traceback/frame escape counterexamples refuse. |
| Code P2-2 — duplicate parameter sets | **CLOSED** | Parameters are pinned at acquisition; executable paths use the stored detached value. |
| Code P2-3 — no ordered/one-shot step grammar | **CLOSED** | Step ranks, state, and committed publication reject direct, repeated, backward, and post-publication work. |
| Code P2-4 — no-effect reopen leaves old admission live | **CLOSED** | Admission/coordinator epochs invalidate old handles and leases on proof-bearing reopen. |
| Code P2-5 — buffer provenance not bound | **CLOSED** | Exact envelope, registration, admission, digest, parameters, binding, queue, cursor, operation, and permit are checked. |
| Code P2-6 — worker command absent from ownership | **CLOSED on its original dispatch/dequeue counterexample** | Exact command/worker/authorization ownership and current-worker checks hold. New `P2-1` concerns the previously missing post-worker lifecycle half. |
| Code P2-7 — privileged kinds default to QUERY | **CLOSED** | Read operation kinds use exhaustive registry-owned capability derivation; unsupported privileged acquisition refuses. |
| Code P2-8 — close without drain/fence | **CLOSED** | Closed local transition grammar and ancestry barriers reject premature finalization while peers remain isolated. |
| Code P2-9 — activation rollback without proof | **CLOSED** | Recovery and unused withdrawal require exact binding/epoch/fence-bound proof. |
| State P2-1 — forgeable generation permits | **CLOSED** | Permits are sealed exact issuer identities; forged, wrong-owner, and replay release preserve counts. |
| State P2-2 — CLOSED with live buffer permit | **CLOSED on the original queued-buffer path** | Close invalidates selected queued permits exactly once and retains active handoffs. |
| State P2-3 — buffer exchange provenance | **CLOSED** | Copied, cross-registration, cross-admission, stale, and replay exchanges refuse without count mutation. |
| State P2-4 — bypass/repeated publication, including expanded revocation vector | **CLOSED** | Exact publication barriers reject bypass, repetition, revocation, expiry, epoch, binding, and fence changes before visibility. |
| State P2-5 — absence as activation proof | **CLOSED** | None, stale, mismatched, and wrong-fence proof inputs preserve the activation state; ACTIVE has no reset edge. |
| State P2-6 — entry-only migration indeterminate state | **CLOSED on the original post-effect paths** | Exact proof supports requested-next success, authoritative full rollback/no-effect with a new epoch, and binding non-reuse. |
| State P2-7 — caller-selected operation capability | **CLOSED** | Operation kind determines capability; query-only contexts cannot acquire privileged effect authority. |
| State P2-8 — mutable parameters after acquisition | **CLOSED** | Closed consumers observe only acquisition-pinned parameters. |
| State-Supp-P2-1 — rejected transfer mutates ownership | **CLOSED** | Illegal transfer validates before mutation; original owner/state/count remain usable and unchanged. |

### Correction1/F1–F10 closure table

| Remediation package and all mapped report IDs | Result on MANIFEST-3 |
|---|---|
| F1 — `Code2 P2-1`, `State2 P2-6`, `OriginCode1 P2-1 residual` | **CLOSED.** Ordinary callbacks were removed from raw-plan and uncommitted-step boundaries; fixed consumers commit before return. |
| F2 — `Code2 P2-2`, `State2 P2-1` | **Original counterexamples CLOSED; package residual OPEN as P2-2.** Two successful ranges now use separate produced/delivered cursors and one FIFO head. A refused active head still advances delivery falsely, so the required rejection vector is not closure-complete. |
| F3 — `Code2 P2-3` | **CLOSED.** ACTIVE_UNUSED withdrawal retains and compares the exact successful activation fence. |
| F4 — `State2 P2-2` | **CLOSED.** Drain uses a sealed attempt, frozen participants, exact per-participant barriers/acks, and refuses stale, duplicate, or skipped acknowledgements. |
| F5 — `State2 P2-3` | **CLOSED on its candidate-provenance counterexamples.** Initial and refresh candidates are sealed, frozen, exact-lease, exact-operation, and one-shot. New `P2-3` is the omitted neutral outcome, not caller-supplied candidate provenance. |
| F6 — `State2 P2-4` | **CLOSED.** Nested/total independent operation kinds are absent; derived commands remain ordinal-bound under one parent lease and permit. |
| F7 — `State2 P2-5` | **CLOSED.** Migration and recovery require exact generation `old + 1`. |
| F8 — `OriginState1 State-Closure-P2-1` | **CLOSED.** Pre-effect reopen requires a sealed current-attempt no-effect proof plus every participant acknowledgement. |
| F9 — `OriginCode1 P2-6 residual` | **CLOSED.** Dequeue and each effect validate the trusted actual current worker; caller-object impersonation does not consume an ordinal. |
| F10 — `OriginCode1 P2-3 residual/new bounded route` | **CLOSED.** Initial/refresh publication validates exact destination queue ancestry, local state, and queue state at the final barrier. |

Other attacked invariants held:

- Generation permits and buffer permits remained exact issuer-owned identities with conserved counts on rejection and replay.
- Immutable ancestry and local close selection did not spill into unrelated peers.
- Queued cancellation still loses cleanly to dequeue; active handoffs remain charged through containment.
- Migration could not begin before global zero and all frozen participant acknowledgements; stale/cross-attempt barriers and no-effect proofs refused mutation-free.
- The active protocol epoch survived close, migration, recovery, and binding non-reuse.
- ACTIVE_UNUSED withdrawal required the original physical-fence identity; ACTIVE remained irreversible after first open.
- Snapshot candidates rejected fabrication, copying, reuse, cross-lease substitution, stale queue targets, and post-fence publication.
- Parent-derived commands did not obtain independent permits or terminal/publication authority.
- Worker effect authorization checked original context validity, host epoch, exact runtime/lease/command/worker/binding/fence, actual current worker, and one-shot ordinal consumption.
- Fixed consumer products did not expose raw plans or reusable executable authority.

Those successful attacks do not cure the three findings above.

## 3. Risks and next action

The expressly deferred production evidence remains deferred rather than reported as defects: real database snapshot provenance, production resolver/rebuild provenance, whole-program static data-flow proof, real async/thread/process synchronization, locks, physical fencing, crash/restart durability, credentials, activation, and public W3 naming. The existing W1 terminal wrong-method P3 also remains outside this amendment.

The single required next action is to **STOP this lane and obtain an operator redesign-or-accept decision for P2-1**. The review-loop cap and the controlling prompt prohibit treating another automatic architecture patch as routine remediation after final correction2 of2.

If the operator chooses redesign, that redesign must also resolve bounded `P2-2` and `P2-3`, freeze a new exact tuple, and receive fresh independent dual-axis review plus originating counterexample closure. The present tuple must not be accepted or landed as the W1/A11 contract amendment.
