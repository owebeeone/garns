# W2 admission-lifetime replacement overlay

**Status:** operator-authorized replacement design for independent review; not
accepted and not implementation authority  
**Date:** 2026-10-04  
**Scope:** additive lifetime overlay on the stopped W2 design

## 1. Decision, base and precedence

This document replaces only the admission-lifetime parts of
`W2-QueryPlanningDesign.md` at SHA-256
`0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`.
The effective review object is that exact stopped base plus this exact overlay.
Neither document is acceptable or executable alone. Acceptance, if later
recorded by the manager, applies only to the hash-pinned pair and does not
accept an implementation or amend the current W1 bytes.

The stopped object's initial design and two remediation rounds remain
historical facts. This operator-authorized replacement begins with zero
remediations under its own ordinary bounded review; it does not relabel the
stopped object accepted, erase its stop, or reset a cap automatically.

The overlay changes point-in-time verifier resolution into whole-operation
ownership. Everything else in the stopped design remains controlling,
including its logical/result algebra, canonical encoding and resource profile,
function fingerprints, one expression model, authored physical mappings,
query/question split, result-role prerequisite, exhaustive consumers,
refusals, ownership gaps and nonclaims.

### 1.1 Exact supersession map

| Base section and quoted clause | Overlay disposition |
|---|---|
| §5.3: “The verifier resolves a handle only when exact object identity is registered, runtime identity and epoch match, record is OPEN, binding/origin/generation remain current, and the full provenance key still matches. It then returns the private `Plan` to the backend's non-public lowering path.” | **Replaced.** The verifier atomically acquires an exact-instance operation lease. No verifier or lease returns, unwraps or caches a raw `Plan`; the registry invokes guarded plan consumers while the lease owns the operation. See §§3–5. |
| §5.3: “Changing any component, reopening/migrating the binding, changing a function fingerprint, or closing the runtime revokes all matching records and increments the registry epoch.” | **Refined.** Logical revocation blocks new lease acquisition but does not falsely erase existing ownership. Graceful drain permits already-owned operations to finish under their pinned semantics; hard fencing suppresses later steps/publication and retains containment until authoritative quiescence. See §§6–7. |
| §5.3: “Runtime close marks every record CLOSED before pool/backend close.” | **Replaced.** Close first enters drain, stops new acquisitions and waits. `CLOSED` is publishable only after operation leases, contained workers, delivery handoffs and relevant A7 identities are resolved as specified in §7. |
| §5.3: “Migration/generation change revokes the old binding set before publishing the new set.” | **Replaced.** A deployment-wide exclusive generation fence must first stop new old-generation leases and drain all existing old-generation execution and delivery ownership across every participating runtime/connection. Migration effects and next-generation publication cannot begin otherwise. See §8. |
| §5.3: “Question initial snapshot, subscription creation and every refresh retain and pass the same handle; they never retain/extract a raw plan.” | **Refined.** The reusable admitted handle remains, but each finite snapshot, refresh and delivery/handoff unit acquires its own operation lease. Idle subscriptions hold no execution lease. See §9. |
| §5.3: “Backend internal child/nested/total statements are derived only during the already-verified operation and cannot become independent public plan consumers.” | **Strengthened.** Each such statement and every fetch/assembly/publication continuation remains within the parent lease; no derived primitive can outlive it or cache a raw plan. See §§4–5. |
| §5.3 migration ordering steps and `plan_admission_v1` handshake | **Replaced where named.** Staged enablement requires the lifetime protocol handshake `plan_admission_lifetime_v1`, deployment-wide generation fencing and fail-closed old/raw/mixed paths. The earlier result-role prerequisite is unchanged. See §10. |
| §6 pipeline steps “backend entry resolves handle through its bound verifier” through “adapter execution” | **Replaced.** One atomic acquisition precedes lowering; the lease spans lowering, queued dispatch, adapter start and all work, snapshot/cursor work, assembly and public publication. See §5. |
| §8: “One admitted handle/registry record is cached” and “every refresh pass[es] that same object” | **Refined.** The handle/record may be reusable while current; each execution unit has a unique lease and revalidates current authority/binding/generation at acquisition and publication barriers. See §9. |
| §10 steps 9–10, the bypass/lifecycle vectors | **Extended.** The original vectors remain regression obligations and gain all lifetime pause/race vectors in §11. |
| §11 admitted-handle/verifier ownership row and §12 final W1 prerequisite | **Replaced in protocol scope only.** The future W1 amendment must define admitted handles, lease/verifier/result roles and lifecycle outcomes together. Runtime owns the registry and local leases; a deployment generation coordinator owns cross-runtime fencing; backends only consume contract capabilities. See §10. |

No other base clause is superseded. In particular, this overlay does not alter
the five result vectors, `garns.plan/1`, `garns.plan-limits/1`, the nine function
goldens, footprint semantics, SQLite lowering semantics, authored storage,
question restrictions, or the requirement to refuse executable W2 projection
until the structural result-role amendment exists.

## 2. Objects, identities and non-escape boundary

There are two distinct capabilities:

- `AdmittedReadHandle` is a reusable, opaque identity for one admitted
  plan/provenance/binding record. It is not an operation and holds no lifetime
  fence by itself.
- `ReadOperationLease` is an opaque exact-instance identity for exactly one
  finite operation unit. It owns that unit from atomic acquisition through
  terminal publication or retained containment. It is neither reusable nor
  transferable by copying.

Both are issuer-created, exact-type, exact-object-identity, noncopyable,
nonserializable, immutable handles with no claims, plan, issuer, registry,
runtime, binding, epoch or generation exposed by fields, representation or
duck-typed protocol. A lookalike, subclass, reconstruction, deserialized value,
structural copy or token copied from another registry refuses.

The runtime-owned `PlanAdmissionRegistry` privately stores each admitted
record's exact W1 `Plan`, complete provenance cache key, exact runtime-instance
identity, registry epoch, binding identity and admission state. A separate
private lease record stores:

```text
OperationIdentity = (
  exact runtime identity,
  monotonically unique runtime operation sequence,
  qualified deployment,
  binding generation,
)

lease record = (
  exact lease object identity,
  exact admitted-record identity,
  OperationIdentity,
  operation kind,
  owner identity,
  lease state,
  deployment shared-generation permit,
  authority/binding/provenance evidence,
  optional A7 transaction identities,
  completion record,
)
```

The sequence is never caller-selected or reused, including after completion.
Reads without write transactions still have an `OperationIdentity`; an empty
transaction-identity set does not make them invisible to close or migration.

The contract-only `PlanAdmissionVerifier` exposes acquisition and lifecycle
operations, not plan resolution:

```text
acquire(handle, operation_kind, parameters, context) -> ReadOperationLease
run_plan_step(lease, exact_step, continuation) -> guarded result
transfer_owner(lease, expected_owner, worker_or_containment_owner) -> None
complete(lease, outcome) -> None
```

Names are internal and provisional. `run_plan_step` is a lexical registry
invocation: the registry supplies the private plan only to a closed exact
consumer while holding lease ownership. The continuation cannot return a
`Plan`, `FrozenPlanRoot`, plan-bearing wrapper, lowerer closure or reusable
claim bag. Its permitted outputs are closed step products such as bound SQL,
opaque adapter commands, typed row fragments or final assembled values, and
those outputs remain tagged to the same operation/generation. A consumer may
not retain the plan in an object, closure, cache, task local or command.
Static import/data-flow checks and hostile consumer tests must fail any public
or backend primitive that accepts, returns, stores or caches raw `Plan` beyond
this lexical boundary. Compiler and backend still do not import the runtime;
the verifier/lease interfaces remain contract foundations implemented by the
runtime and passed to the backend at construction.

## 3. Closed states and legal transitions

### 3.1 Admission and binding states

An admitted record has exactly `ADMITTED`, `DRAINING`, `REVOKED`, or
`RETIRED`. A deployment binding has exactly `CURRENT`, `DRAINING_OLD`,
`MIGRATING`, `MIGRATION_INDETERMINATE`, or `RETIRED`. `CURRENT` carries the
exact current `BindingIdentity`; it is not a generation-independent state.

| State | New leases | Existing leases | Publication |
|---|---|---|---|
| record `ADMITTED`, binding `CURRENT` | allowed after full atomic validation | run under pinned generation | allowed after barriers |
| record `DRAINING`, binding `DRAINING_OLD` | refused | graceful policy only: finish under old pinned semantics | allowed only before exclusive cutover and only with old-generation cursor |
| record `REVOKED` | refused | must be terminal or `CONTAINED`; no new adapter step | suppressed |
| record `RETIRED` | refused | none | impossible |
| binding `MIGRATING` | refused for old and next generation | none for old generation | only migration's governed/accounted effects |
| binding `CURRENT` after successful cutover | published next generation only | next generation only | next generation only |
| binding `MIGRATION_INDETERMINATE` | refused | containment/reconciliation only | no next-generation publication |

Legal record edges are `ADMITTED -> DRAINING -> REVOKED -> RETIRED` and
`ADMITTED -> REVOKED -> RETIRED` for an immediate hard fence. Legal binding
edges are:

```text
CURRENT -> DRAINING_OLD -> MIGRATING -> CURRENT       (requested next binding)
CURRENT -> DRAINING_OLD -> CURRENT                 (pre-effect refusal/reopen)
MIGRATING -> MIGRATION_INDETERMINATE
MIGRATION_INDETERMINATE -> CURRENT                 (authoritative success at requested next binding)
MIGRATION_INDETERMINATE -> CURRENT                 (authoritative full rollback/no effect, new epoch)
MIGRATION_INDETERMINATE -> RETIRED                 (authoritative non-reuse)
CURRENT -> RETIRED
```

There is no rollback from `MIGRATING` to the old `CURRENT`: after any migration
effect, only authoritative success may publish the requested next binding;
otherwise the deployment is indeterminate and refuses ordinary work. Reopening
the old generation is allowed only from `DRAINING_OLD`, after authoritative
proof that no migration effect began, with the same binding/generation and a
new admission epoch; old handles and leases remain invalid.

### 3.2 Lease states

A lease has exactly `ACQUIRED`, `QUEUED`, `RUNNING`, `PUBLISHING`,
`CONTAINED`, `SUCCEEDED`, `REFUSED`, or `CANCELLED_CONFIRMED`.

| From | Legal targets | Meaning |
|---|---|---|
| `ACQUIRED` | `QUEUED`, `RUNNING`, `REFUSED`, `CANCELLED_CONFIRMED`, `CONTAINED` | ownership exists before work can be queued |
| `QUEUED` | `RUNNING`, `CANCELLED_CONFIRMED`, `CONTAINED` | not-started cancellation needs authoritative dequeue evidence |
| `RUNNING` | `PUBLISHING`, `SUCCEEDED`, `REFUSED`, `CONTAINED` | lowering/adapter/fetch/snapshot/assembly work |
| `PUBLISHING` | `SUCCEEDED`, `REFUSED`, `CONTAINED` | final barrier and public handoff |
| `CONTAINED` | `SUCCEEDED`, `REFUSED`, `CANCELLED_CONFIRMED` | authoritative owner still holds possibly resumable work |
| terminal states | same terminal state only | identical completion is idempotent |

`SUCCEEDED`, `REFUSED`, and `CANCELLED_CONFIRMED` are terminal. A second
identical completion for the same exact lease and complete outcome is
idempotent. A different terminal outcome, wrong lease, wrong operation
identity, wrong owner or terminal reuse is a conflict and cannot mutate state.
Exceptions before any resumable work exists complete `REFUSED`; authoritative
queued removal completes `CANCELLED_CONFIRMED`. Cancellation, timeout, a
`finally` block, task disappearance, connection loss or an exception after
dispatch is not proof of quiescence: ownership transfers to `CONTAINED` unless
the adapter/worker supplies authoritative completion. Lease record removal is
allowed only after a terminal state and release of its generation permit.

## 4. Atomic acquisition, ownership and lock order

Acquisition uses this global order; no path may invert it:

1. deployment generation gate for the exact `QualifiedDeployment`;
2. runtime admission-registry lock;
3. connection/worker queue ownership lock, only when dispatching;
4. A7 transaction commit fence, only for governed effects.

The acquisition linearization point is the single registry mutation that,
while a shared generation permit is held, validates the exact handle and
record, runtime identity, admission epoch, `CURRENT` binding/generation, full
provenance key, operation kind, parameters and current A11 authority, allocates
an unused `OperationIdentity`, inserts the `ACQUIRED` lease record and charges
it to the runtime and deployment counts. Validation failure inserts nothing.
The shared permit is stored in the lease record and cannot be released by the
caller.

Dispatch's linearization point is one queue-lock mutation that transfers the
lease owner from caller/runtime to the exact worker command and changes
`ACQUIRED` to `QUEUED`. Dequeue changes `QUEUED` to `RUNNING` and transfers to
the exact worker. A queued cancellation succeeds only by atomically removing
that command while it still owns `QUEUED`; otherwise cancellation transfers
ownership to containment and requests interruption. Worker-to-runtime result
handoff and worker-to-containment transfer are likewise compare-and-transfer
operations naming the expected current owner. No caller `finally` releases a
lease owned by a worker.

The publication linearization point is an atomic registry/barrier operation
that changes `RUNNING` to `PUBLISHING`, revalidates exact owner, live lease,
authority, pinned binding/generation and applicable cursor, then records the
handoff as committed before the value becomes caller-visible. Completion then
changes `PUBLISHING` to `SUCCEEDED` and releases counts/permit. If the barrier
fails, nothing becomes public and the lease refuses or remains contained.

Acquisition is therefore not a check followed by unprotected work. Every
operation has ownership before it can queue, and the generation permit plus
lease survives every await, worker boundary and continuation until terminal
publication or authoritative containment completion.

## 5. Whole-operation coverage and barriers

One lease covers the complete finite unit:

```text
atomic acquire
  -> semantic/static capability and binding checks
  -> parameter/default binding
  -> lowering and all root/child/nested/total command derivation
  -> queued dispatch and adapter start
  -> every execute/fetch/child/total step
  -> snapshot transaction, high-water read and registration where applicable
  -> row/result/total assembly
  -> authority + lease + generation + cursor publication barrier
  -> public result, snapshot, durable registration or delivery handoff
  -> terminal completion/release
```

Before lowering, queue insertion, adapter start, each independently scheduled
fetch/child/total command, snapshot high-water read, registration commit,
assembly handoff and public publication, `run_plan_step` checks exact live
lease identity and owner. It also revalidates A11 authority immediately before
every database effect and at the final publication/handoff barrier; expiry or
invalidation cannot ride the lease past those boundaries. Under graceful drain it accepts an existing lease's
pinned old generation; under a hard fence it refuses a new step and transfers
  possibly resumable work to containment. A command already inside an
  uninterruptible adapter call may finish privately, but its result is
  discarded and it cannot begin another command or publish. No command can be detached from the
lease, and no child/total result can be cached for another operation.

A snapshot succeeds only if rows, high-water cursor and durable registration
were produced under one lease and the same qualified deployment/generation.
If a fence or generation mismatch occurs before its publication barrier, the
entire candidate is discarded and returns a typed refusal/refetch outcome; it
never publishes old-plan rows with a new cursor.

The success path remains possible: an exact current handle acquired while
`CURRENT`, with genuine authority and valid parameters, proceeds through all
steps under its one lease and publishes exactly once. Lifetime fencing must not
turn correctly admitted uncontended work into a permanent refusal.

## 6. Logical revocation, graceful drain and hard fencing

Logical revocation and final fencing are distinct:

- **Graceful drain** changes runtime/records to `DRAINING` and the binding to
  `DRAINING_OLD`. It blocks all new leases at the drain linearization point.
  Leases acquired earlier keep their shared generation permits and may perform
  later adapter/fetch/assembly/publication steps under their pinned old
  semantics. They must finish before the deadline. No next generation or
  `CLOSED` state is visible during this interval.
- **Hard fence** changes remaining records to `REVOKED`. From its linearization
  point, no remaining lease may start another adapter command or publish a
  result/delivery. Already running or non-killable work transfers to
  `CONTAINED`; its private results are discarded. The fence is logical
  suppression, not proof that the worker stopped, and does not release its
  generation permit.
- **Final fence** exists only when every relevant lease is terminal, every
  contained worker is authoritatively quiescent, every delivery handoff is
  terminal, and A7 transaction knowledge satisfies its independent rules.
  Only final fencing permits `CLOSED`, old-generation retirement or next-
  generation publication.

These modes are not simultaneous promises. Graceful drain deliberately allows
old admitted work to finish and publish before final invalidation. If policy or
deadline switches to hard fence, later work and publication are suppressed,
but resources remain owned until quiescence. Migration never uses hard fencing
to pretend old work is gone; failure to drain before effects makes migration
refuse.

## 7. Close, deadline, cancellation and non-killable workers

Runtime/pool/connection close first installs the graceful-drain barrier and
closes the A8 late-commit fence. It then waits within the configured deadline
for lease and worker quiescence. The exact outcomes are:

| Condition at deadline/finalization | Outcome and retained ownership |
|---|---|
| no leases, no contained workers, no unresolved A7 identities | `CLOSED` |
| quiescent operations but one or more unresolved A7 transaction identities | accepted A7/A8 `UNRESOLVED` with those identities |
| any queued/running/publishing/contained lease or worker may resume | `NONQUIESCENT` plus exact `OperationIdentity` values and any A7 identities |

The future W1 amendment must extend close knowledge to retain read-operation
identities; it cannot encode a no-transaction read as `CLOSED` merely because
the current `CloseOutcome.unresolved` tuple accepts only transaction
identities. Operation identities and transaction identities are separate sets.
An operation may be quiescent while transaction knowledge is unresolved, or a
non-killable read worker may be nonquiescent with no transaction identity.

Force close switches remaining leases to hard-fenced containment and may
discard connections from reusable pools, but returns `NONQUIESCENT` while any
worker can resume. It cannot assert thread termination, rollback, release the
shared generation permit or destroy registry evidence. Reopen creates a new
runtime identity, registry and epoch. Old handles and leases never become valid
there, and the new runtime cannot bypass the retained deployment permit of an
old contained worker.

For writes, A7/A8 remain independently controlling: shutdown closes the commit
authorization fence; work that had not requested commit cannot request it
later; commit-requested identities retain authoritative terminal knowledge;
indeterminate outcomes stay retained; matching repeated resolution is
idempotent and conflicting resolution refuses. Lease completion never invents
commit knowledge, and commit resolution never proves worker quiescence.

## 8. Deployment-wide migration fence

The generation fence is keyed by exact `QualifiedDeployment`, not runtime,
process, pool, cache or connection. Every participating runtime and borrowed
connection must join the same deployment coordinator at open and negotiate
`plan_admission_lifetime_v1`. Each operation holds a coordinator-issued shared
permit for its exact generation. PostgreSQL realizes the coordinator with the
qualified-deployment advisory-lock and durable-generation protocol on dedicated
coordination connections. Supported file-backed SQLite uses a canonical
database-file identity, a process-wide shared/exclusive coordinator covering
every runtime/connection for that file, and an interprocess lock plus durable
generation record; in-memory SQLite is necessarily confined to its one process
coordinator. A SQLite deployment that cannot establish the same coordination
identity across its participating processes refuses multi-process open rather
than using local counts. A process-local cache count alone is never sufficient
for a deployment admitted across processes. Any instance that cannot prove
participation, current generation or protocol support refuses open/work.

Migration ordering is exact:

1. acquire the finite-wait deployment migration mutex before any runtime or
   registry lock;
2. validate the request, expected old binding/digests/generation, authority,
   effect class and governed accounting while still effect-free;
3. atomically change the coordinator to `DRAINING_OLD`, preventing every
   participant and connection from acquiring a new old-generation shared
   permit; notify local registries to enter graceful drain;
4. wait within the migration-lock deadline until the coordinator proves zero
   old-generation execution and delivery permits across all participants;
5. if the count does not reach zero, refuse before any migration effect,
   release the exclusive request and reopen the same old generation only with
   authoritative no-effect proof and a new admission epoch;
6. acquire the exclusive generation permit and change to `MIGRATING`;
7. perform only the A12-classified migration: metadata proof with no bound
   data/shape change, or atomically governed/accounted DML/DDL effects;
8. durably publish the exact requested next binding, generation and its
   ledger/revision boundary while holding the exclusive permit;
9. invalidate old handles, durable subscription registrations and buffers,
   change to `CURRENT` carrying the requested next binding, then release the
   exclusive permit so next-generation shared acquisitions may begin.

No migration effect, DDL, backfill, generation publication or next-generation
plan admission occurs before step 6. Online/mixed-version schema operation is
not added. If failure occurs before step 6, it is a typed no-effect refusal and
may reopen old generation as stated. Failure during or after step 7 is
`MIGRATION_INDETERMINATE`: ordinary execution, delivery, old reopening and next
publication all refuse until authoritative recovery establishes the exact
outcome. Rollback is allowed only when the migration implementation provides
authoritative rollback/no-effect evidence; absence of a success response is
not that evidence.

This fence covers SQLite and PostgreSQL execution, initial snapshots,
refreshes, nested/total work, buffered delivery handoffs and every connection
for the qualified deployment. External capture remains deferred. Governed
migration effects remain subject to the accepted accounting rules.

## 9. Subscription, cursor and buffer lifecycle

An idle subscription retains only an opaque admitted handle identity, bound
parameters, exact binding/generation, durable registration identity and cursor;
it holds no execution or delivery lease and therefore cannot block close or
migration forever.

Finite units are separately leased:

- initial open uses one snapshot/registration lease through atomic publication
  of `(rows, S, registration)`;
- each refresh uses one lease through exact `(rows, H)` evaluation, cursor
  advancement and candidate-batch creation;
- each public `__anext__` handoff uses one delivery lease from dequeue through
  the post-await A11 check and caller-visible return.

Refresh revalidates the handle, binding/generation and authority at acquisition.
It may enqueue only an immutable `BufferedDelivery` containing the exact
qualified deployment, generation, admitted-record identity, plan digest,
`previous`, `triggered_by`, `observed_through`, rows and durable advancement
state from that same leased snapshot. It contains no plan or lease. Cursor
advancement and enqueue follow A6's atomic rule; a neutral refresh advances the
internal cursor without creating a delivery.

Successful enqueue atomically replaces the refresh lease's publication charge
with a finite `BufferedDeliveryPermit` bound to that exact envelope identity
and generation. The permit exposes no plan and authorizes no execution; it only
prevents cutover from overtaking a not-yet-decided old-generation handoff.
Dequeue atomically exchanges it for the delivery lease. Discard/overflow/close
atomically invalidates the envelope and releases it. Migration drain does not
wait forever for an idle consumer: after stopping new refreshes it invalidates
all still-queued old-generation envelopes, releases their permits, and requires
active delivery leases to finish or quiesce before effects.

Delivery lease acquisition validates every envelope field against the current
subscription registration and generation. The publication barrier repeats the
A11 post-await check and generation/lease check. An old-generation, stale-plan,
copied, already-delivered or mismatched buffer is never relabeled; it is
discarded and terminates with typed `RefetchRequired`/generation mismatch.
Duplicate completion for the exact delivery identity is idempotent; a second
handoff or conflicting cursor completion refuses.

The durable registration is also generation-bound. Exclusive migration
cutover invalidates the old registration atomically with old handles and queued
buffers. A still-open idle subscription therefore performs the A6 refetch and
registration handshake in the new generation before another refresh; it never
silently carries its old cursor or registration forward.

On graceful close, no new refresh lease starts. Policy may finish already
leased refresh and delivery units before final close. At deadline/hard fence,
queued buffers are invalidated and discarded, active handoffs become contained,
and no later caller-visible return is allowed. On migration drain, buffered old
generation deliveries count as delivery permits: they must be handed off before
exclusive cutover or invalidated and authoritatively quiesced before migration
effects. They cannot survive cutover. `CLOSED` guarantees there is no active
lease, contained operation, queued valid buffer, live iterator handoff or
future delivery from that runtime; it does not claim that an external consumer
has processed a value returned before the close barrier.

## 10. Required W1 amendment and staged enabling

The frozen W1 tuple remains unchanged by this design. Before any executable W2
integration, one separately scoped and independently reviewed W1 amendment
must define, as one coherent protocol/result ownership change:

1. structural result roles and the nested-owner representation already
   required by the stopped base;
2. exact `AdmittedReadHandle`, `ReadOperationLease`, verifier and registry
   ownership contracts, with no raw-plan executable signature or unwrap;
3. operation identities and close outcomes capable of retaining nontransaction
   reads independently from A7 transaction identities;
4. the state enums, transitions, owner-transfer/completion rules, graceful and
   hard fences, subscription unit leases and deployment-generation permit;
5. amended execute, snapshot, subscribe, refresh, iterator-delivery,
   migration, pool/connection close and containment handshakes;
6. exact refusal codes for admission required, stale/released/copied/cross-
   runtime/cross-binding/cross-generation lease, lease owner conflict,
   operation outcome conflict, drain/fence, generation and refetch cases.

Integration remains future W3/W4/W5 ownership, not W2 document authority:

1. add and accept the W1 result/lifetime protocol amendment;
2. implement the deployment coordinator, registry, lease state machine and
   containment before enabling plan execution;
3. construct every backend/pool/connection with the exact bound verifier and
   generation coordinator; require `plan_admission_lifetime_v1` at open;
4. change execute/snapshot/subscribe/refresh/delivery and every child/total
   continuation to lease-only guarded calls;
5. make all legacy bare-plan, point-verifier, raw-plan, old-handshake and mixed-
   version paths refuse before lowering or I/O;
6. prove exhaustive consumer/data-flow checks, deployment-wide migration
   fencing and lifecycle vectors before removing old paths or enabling W2.

No stage permits a working legacy path beside reliance on lifetime admission.
Raw `Plan`, the stopped point-in-time verifier result, `plan_admission_v1`
without the lifetime capability, unknown/missing protocol versions and peers
that cannot join the deployment fence all fail closed. Backend/compiler import
direction is unchanged. Public names and W3 Surface remain future.

## 11. Invariant and closure vectors

### 11.1 Original final Safety counterexample

At each pause immediately after acquire and before lowering, queue dispatch,
adapter start, first and later fetch, child/total work, snapshot watermark,
registration, assembly, cursor advancement and public result/delivery
publication, race:

- graceful close, hard/force close and close deadline;
- deployment migration and next-generation publication;
- reopen and registry-epoch change.

The falsifiable result is always one of: the old operation completes and
publishes before final fencing under graceful drain; it is stopped before the
next step and publishes nothing under hard fence; or it remains explicitly
`NONQUIESCENT`/contained. It is never unowned, never uses new generation with
old semantics, never permits `CLOSED`, and never permits migration cutover while
it can resume. The originating final Safety reviewer must verify this exact
counterexample against the composed base-plus-overlay object.

### 11.2 Complete design-level vectors

| Vector | Required observation |
|---|---|
| pause after acquisition, before every boundary above | lease remains charged; close/cutover cannot pass it |
| queued cancellation | authoritative dequeue gives `CANCELLED_CONFIRMED`; dequeue race transfers to worker/containment |
| non-killable SQLite worker past deadline | hard-fenced `NONQUIESCENT`, exact operation retained; current call may finish privately, but no new command, publication or late commit request |
| read with no transaction identity | still prevents `CLOSED`/migration through its operation identity |
| A7 commit-requested write | lease and commit fence both retained; neither invents the other's proof |
| cross-runtime migration with two pools/connections | exclusive fence waits for both deployment-wide permit sets, not one cache |
| stale/cross-runtime/cross-binding/cross-generation handle | acquisition refuses without a lease |
| copied/fabricated/released lease | every step refuses before lowering/I/O/publication |
| duplicate identical completion | idempotent, counts released once |
| conflicting completion or wrong owner | refuses and preserves original state/counts |
| exception before dispatch | terminal refusal and release |
| exception/cancellation after dispatch | containment until authoritative worker quiescence |
| initial snapshot race | rows, cursor and registration share one generation or whole unit refetches |
| delayed buffered delivery across drain/migration | old envelope delivered before cutover or invalidated; never handed off after cutover |
| idle subscription | holds no execution permit; close/migration progresses |
| refresh neutral result | cursor advances under one lease, no batch |
| correctly admitted success | exact current lease completes every step and publishes once |

Original base attacks remain mandatory: bare/extracted/caller-constructed plans;
same-origin semantic mutants; copied/fabricated handles; resource limits;
mixed versions; hidden result keys; nested/total consumers; authority expiry;
authored physical-name hostility; function fingerprints; and complete
exhaustive registries. Closing the lifetime finding must not reopen them.

### 11.3 Future static and executable evidence

Future tests must instrument a barrier at every pause point, deterministically
race each transition, and assert registry state, owner, operation/deployment
counts, adapter call count, publication count and buffer/cursor generation.
Property/state-machine tests enumerate every legal/illegal transition and all
duplicate/conflicting completions. Multi-runtime tests use independently opened
participants for one qualified deployment. Worker tests retain a genuinely
blocked non-killable command. Subscription tests delay before and after await,
buffer across drain, invalidate authority, overflow/refetch and migrate.

Syntax-aware architecture checks enumerate every function that reaches plan
lowering, adapter invocation, fetch, assembly, snapshot registration, cursor
advance or public publication. They fail on raw-plan types/returns/caches,
point-only resolution, unleased continuations, missing publication barriers,
lock-order inversions, operation removal before terminal state, local-only
migration counts, or a close outcome unable to name nontransaction work.

These are design obligations, not claims of real database, thread, async,
crash, PostgreSQL advisory-lock or supported-version proof. Those remain at
their implementation gates.

## 12. Preserved scope and nonclaims

This overlay preserves CPython >=3.11, supported SQLite >=3.35 with JSON1,
PostgreSQL-primary 15–18 and verified later stable majors, async-only future
database runtime, in-process provider-neutral trust, one convergent product,
the unchanged grammar and `unenforced`, and the governed-write boundary.

External capture, cryptographic/named-provider integration, PostgreSQL
execution, public API names, W3 Surface, W1 Code P3 assigned to W3, W2
implementation, database/service/dependency work and unrelated refactors remain
deferred. No online or mixed-version schema support is introduced.

This design does not modify W1, source, tests, ADRs or grammar; run a build or
database; prove worker/database behavior; accept itself; close the stopped
object; launch an amendment or implementation; or authorize Git/GWZ work. Its
next action is manager pinning and fresh independent Consistency/Safety review,
including originating final Safety closure. GO/GO plus that closure can accept
only the exact base-plus-overlay design tuple. A separately authorized W1
amendment and implementation execution brief remain prerequisites.
