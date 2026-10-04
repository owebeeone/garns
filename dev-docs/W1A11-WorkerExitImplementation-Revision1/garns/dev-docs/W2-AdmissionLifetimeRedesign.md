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
historical facts. This replacement has now used its two permitted consolidated
architectural remediations; no third architectural correction is authorized.
It does not relabel the stopped object accepted, erase its stop, or reset a cap
automatically. The initial and remediation-1 overlays remain preserved byte-
identically in `W2-AdmissionLifetimeRedesign-Initial.md` and
`W2-AdmissionLifetimeRedesign-Revision2.md`.

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
  local resource ancestry,
  issuer-private worker-command authority record if dispatched,
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

Public `TrustedContext` remains task-bound exactly as accepted in A11; a lease
or owner transfer never transfers it. Worker execution instead requires the
separately amended issuer-private command handshake defined in §5.1. Current
A11/W1 has no such path, so worker-backed execution remains disabled until that
authority extension is separately reviewed and accepted.

## 3. Closed states and legal transitions

### 3.1 Local admission, resource and deployment states

Three independent closed state machines are mandatory.

An admitted record has exactly `ADMITTED`, `DRAINING`, `REVOKED`, or
`RETIRED`. A local lifecycle resource—runtime, pool, connection or
subscription—has exactly `LOCAL_OPEN`, `LOCAL_DRAINING`, `LOCAL_FENCED`, or
`LOCAL_CLOSED`. A deployment binding has exactly `CURRENT`, `DRAINING_OLD`,
`MIGRATING`, `MIGRATION_INDETERMINATE`, or `RETIRED`. `CURRENT` carries the
exact current `BindingIdentity`; it is not a generation-independent state.

| State | New leases | Existing leases | Publication |
|---|---|---|---|
| record `ADMITTED`, all local ancestors `LOCAL_OPEN`, deployment `CURRENT` | allowed after full atomic validation | run under pinned generation | allowed after barriers |
| local ancestor `LOCAL_DRAINING` | refused through that resource only | descendant graceful policy may finish | allowed before that local final fence |
| local ancestor `LOCAL_FENCED` or record `REVOKED` | refused through that resource only | terminal or `CONTAINED`; no new command | suppressed through that resource |
| local ancestor `LOCAL_CLOSED` or record `RETIRED` | refused | none attributable to that resource | impossible |
| deployment `DRAINING_OLD` | globally refused for old generation | graceful old-generation work may finish | old generation only before exclusive cutover |
| deployment `MIGRATING` | globally refused for old and next generation | none for old generation | only migration's governed/accounted effects |
| deployment `CURRENT` after successful cutover | published next generation only | next generation only | next generation only |
| deployment `MIGRATION_INDETERMINATE` | globally refused | containment/reconciliation only | no next-generation publication |

Legal record edges are `ADMITTED -> DRAINING -> REVOKED -> RETIRED` and
`ADMITTED -> REVOKED -> RETIRED`. Legal local-resource edges are
`LOCAL_OPEN -> LOCAL_DRAINING -> LOCAL_CLOSED` and
`LOCAL_OPEN|LOCAL_DRAINING -> LOCAL_FENCED -> LOCAL_CLOSED`. The same resource
identity never reopens: a later open creates a new exact instance, local epoch
and ancestry. `NONQUIESCENT` and `UNRESOLVED` are close outcomes retaining a
`LOCAL_FENCED` resource, not hidden transitions to `LOCAL_CLOSED`.

Legal deployment edges are:

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
the old generation is allowed only from migration-owned `DRAINING_OLD`, after
authoritative proof that no migration effect began, with the same binding and
generation and a new deployment admission epoch; old handles and leases remain
invalid. Ordinary local close never enters `DRAINING_OLD`, changes the
deployment epoch, retires the binding or invalidates handles in an unrelated
runtime.

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

1. deployment activation/generation gate for the exact `QualifiedDeployment`;
2. local resource gates from runtime to pool to connection/subscription;
3. runtime admission-registry lock;
4. connection/worker or subscription-queue ownership lock, only when needed;
5. A7 transaction commit fence, only for governed effects.

The acquisition linearization point is the single registry mutation that,
while a shared generation permit is held, validates the exact handle and
record, durable lifetime activation epoch, runtime identity, admission epoch,
`CURRENT` binding/generation, every exact local ancestor in `LOCAL_OPEN`, full
provenance key, operation kind, parameters and current A11 authority; it then
allocates an unused `OperationIdentity`, inserts the `ACQUIRED` lease record
with immutable runtime/pool/connection-or-subscription ancestry and charges it
once to every ancestor plus the deployment count. Validation failure inserts
nothing.
The shared permit is stored in the lease record and cannot be released by the
caller.

Resource attribution is exact and immutable. A connection close selects only
leases dispatched to that connection. A pool close selects that pool, its
connections and leases acquired through it. A subscription close selects its
refresh, buffer and handoff resources. A runtime close selects every local
descendant. Releasing a lease decrements each charged ancestor and the
deployment permit exactly once. A locally fenced/nonquiescent descendant stays
registered with its counts, so the deployment coordinator and a later
migration still see it even after its parent rejects new work. No lease,
connection, worker command, subscription or buffer may be reparented or
retargeted to an open sibling after an ancestor begins draining; owner transfer
changes the execution owner only, never the immutable resource ancestry.

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
every task-owned boundary and at the final publication/handoff barrier; each
worker-owned database effect instead uses §5.1's immediate issuer-private
validation without transferring the public context. Expiry or invalidation
cannot ride the lease past those boundaries. Under graceful drain it accepts
an existing lease's pinned old generation; under a hard fence it refuses a new
step and transfers possibly resumable work to containment. A command already
inside an uninterruptible adapter call may finish privately, but its result is
discarded and it cannot begin another command or publish. No command can be
detached from the lease, and no child/total result can be cached for another
operation.

A snapshot succeeds only if rows, high-water cursor and durable registration
were produced under one lease and the same qualified deployment/generation.
If a fence or generation mismatch occurs before its publication barrier, the
entire candidate is discarded and returns a typed refusal/refetch outcome; it
never publishes old-plan rows with a new cursor.

The success path remains possible: an exact current handle acquired while
`CURRENT`, with genuine authority and valid parameters, proceeds through all
steps under its one lease and publishes exactly once. Lifetime fencing must not
turn correctly admitted uncontended work into a permanent refusal.

### 5.1 Issuer-private worker authority

Current A11 validates a public `TrustedContext` only in its exact issuing task.
That handle remains task-bound and is never copied, rebound, stored in a worker
command or made valid in the worker. To reconcile A11 with A8, the future
authority amendment must add an issuer-private handshake with these exact
properties:

1. While the issuing task and context are valid, dispatch asks the trusted
   issuer to create one opaque `WorkerCommandAuthorization` for the exact
   runtime, lease, operation identity, queued command identity, assigned worker
   identity, binding/generation, capability and closed set of effect ordinals.
2. The command-internal authorization object is another empty exact-instance,
   noncopyable, nonserializable identity and is never exposed to an ordinary
   caller. Only the issuer record links it to the original issued-context
   record, validity deadline, host epoch and command; no claims or
   `TrustedContext` move into the command.
3. Queue insertion atomically binds that authorization to the same command and
   lease owner transfer. Cancellation/dequeue, hard fencing, terminal lease
   completion or context invalidation revokes every unused effect ordinal.
4. Immediately before each adapter effect, the exact assigned worker calls an
   issuer-private `validate_worker_effect` with the authorization, lease,
   command and next ordinal. The issuer uses trusted current time/host epoch,
   confirms the original context record is still live and was task-valid at
   dispatch, checks scope/capability plus exact runtime/lease/command/worker/
   generation/fence state, and atomically consumes that ordinal before allowing
   the effect. It does **not** pretend the worker is the public context's task.
5. A later fetch or child/total command receives its own command identity and
   authorization/ordinals through the same guarded dispatch. Reuse for another
   effect, command, lease, worker, runtime, generation or after revocation
   refuses before adapter invocation.

If expiry or invalidation occurs after enqueue but before the worker check, the
effect count remains zero and the lease refuses or enters containment. If it
occurs after a begun uninterruptible effect, A7/A8 and lease containment govern
the result; authority timing does not manufacture rollback or quiescence.
Caller cancellation also revokes unused ordinals before requesting worker
interruption, but cannot release an already-running command.

This is a required, separately reviewed A11/W1 authority-extension amendment,
not an interpretation of current `RuntimeAuthority.validate` and not a source
change authorized here. It preserves the task-bound public context, in-process
trust boundary, zero-staleness checks at effect boundaries and minimum
disclosure. Until that amendment is accepted and integrated, no worker-backed
W2 operation may be enabled.

## 6. Logical revocation, graceful drain and hard fencing

Logical revocation and final fencing are distinct and scoped:

- **Local graceful drain** atomically changes only the selected resource to
  `LOCAL_DRAINING`. A runtime close also changes that runtime's admitted
  records to `DRAINING`; pool, connection and subscription close do not mutate
  reusable runtime-wide admitted records. The local gate blocks new leases
  through the selected ancestry at its drain linearization point. Other
  runtimes/pools/connections remain `LOCAL_OPEN`, their handles/epochs remain
  valid, and the deployment remains `CURRENT`. Earlier descendant leases keep
  their deployment permits and may perform later work/publication under pinned
  semantics before the deadline.
- **Deployment graceful drain** is migration-only. While holding the migration
  mutex, it changes the binding to `DRAINING_OLD` and tells every participant's
  local generation gate to reject new old-generation acquisition. Existing
  leases across all participants may finish before the exclusive cutover.
- **Hard fence** changes the selected resource to `LOCAL_FENCED` and its
  remaining leases to contained/revoked ownership. Runtime hard fence also
  changes its admitted records to `REVOKED`; child-resource hard fence does
  not. From its linearization point, no remaining selected lease may start
  another adapter command or publish a result/delivery. A migration fence is
  deployment-wide.
  Already running or non-killable work transfers to `CONTAINED`; its private
  results are discarded. The fence is logical suppression, not proof that the
  worker stopped, and does not release its generation permit.
- **Final fence** exists only when every relevant lease is terminal, every
  contained worker is authoritatively quiescent, every delivery handoff is
  terminal, and A7 transaction knowledge satisfies its independent rules.
  A local final fence permits only that resource's `LOCAL_CLOSED`. A deployment
  final fence permits old-generation retirement or next-generation publication.

These modes are not simultaneous promises. Graceful drain deliberately allows
already admitted work to finish and publish before the applicable final fence.
If policy or deadline switches to hard fence, later work and publication are
suppressed, but resources remain owned until quiescence. Local close never
changes deployment generation state. Migration never uses hard fencing to
pretend old work is gone; failure to drain before effects makes migration
refuse.

## 7. Close, deadline, cancellation and non-killable workers

Connection, pool, subscription or runtime close first installs its local
graceful-drain barrier over exactly the descendants attributed in §4. A
connection/pool/runtime also closes the A8 late-commit fence for its selected
worker ancestry. It then waits within the configured deadline for only that
resource tree's leases, buffers, handoffs and workers. The deployment remains
`CURRENT`, and unrelated participant acquisition proceeds. Exact outcomes are:

| Condition at deadline/finalization | Outcome and retained ownership |
|---|---|
| no attributed leases/buffers/handoffs, no contained workers, no unresolved A7 identities | `CLOSED`; selected resource becomes `LOCAL_CLOSED` |
| quiescent operations but one or more unresolved A7 transaction identities | accepted A7/A8 `UNRESOLVED` with those identities |
| any queued/running/publishing/contained lease or worker may resume | `NONQUIESCENT` plus exact `OperationIdentity` values and any A7 identities |

The future W1 amendment must extend close knowledge to retain read-operation
identities; it cannot encode a no-transaction read as `CLOSED` merely because
the current `CloseOutcome.unresolved` tuple accepts only transaction
identities. Operation identities and transaction identities are separate sets.
An operation may be quiescent while transaction knowledge is unresolved, or a
non-killable read worker may be nonquiescent with no transaction identity.

Force close switches only remaining attributed leases to hard-fenced
containment and may discard selected connections from reusable pools, but
returns `NONQUIESCENT` while any worker can resume. It cannot assert thread
termination, rollback, release the shared generation permit, unregister the
retained participant or destroy registry evidence. A parent cannot become
`LOCAL_CLOSED` while a descendant is retained. Reopen creates a new exact
resource instance; runtime reopen also creates a new runtime identity, registry
and epoch. Old handles and leases never become valid there, and the new
resource cannot bypass the retained deployment permit of an old contained
worker. Once every selected descendant is terminal, finalization unregisters
only that participant/resource and changes it to `LOCAL_CLOSED`; it does not
change another participant's state or epoch. Only runtime finalization retires
that runtime's admitted records; closing a child resource leaves the handle
usable through another `LOCAL_OPEN` ancestry after fresh acquisition checks.

For writes, A7/A8 remain independently controlling: shutdown closes the commit
authorization fence; work that had not requested commit cannot request it
later; commit-requested identities retain authoritative terminal knowledge;
indeterminate outcomes stay retained; matching repeated resolution is
idempotent and conflicting resolution refuses. Lease completion never invents
commit knowledge, and commit resolution never proves worker quiescence.

## 8. Deployment-wide migration fence

### 8.1 One-time lifetime-protocol activation

The deployment protocol state is exactly `UNACTIVATED`, `ACTIVATING`,
`ACTIVE_UNUSED(epoch)`, `ACTIVE(epoch)`, or `ACTIVATION_INDETERMINATE`.
A handshake or durable marker
written by new binaries is not proof that an already-open legacy process has
stopped. Before any lifetime-dependent W2 execution, the deployment operator
must perform one finite-wait stop-the-world activation under separately
reviewed W3/W4 deployment/runtime ownership.

Activation authority belongs to the deployment operator/control plane, not an
ordinary runtime, caller or cooperative participant. Its authoritative proof
must combine all of the following for the exact qualified deployment:

1. acquire the exclusive maintenance/activation lock and stop application
   admission at the supervisor/orchestrator boundary;
2. use the operator's authoritative process/workload inventory to terminate
   and prove absence of every pre-protocol runtime, rather than asking new
   runtimes for a cooperative census;
3. fence database access held by old binaries: for PostgreSQL, terminate old
   sessions and revoke/rotate the old deployment connection authority before
   issuing replacement authority only to lifetime-capable instances; for
   file-backed SQLite, hold the canonical database's exclusive interprocess
   activation lock and prove no legacy file handle/process can execute; an
   environment unable to provide that physical exclusion refuses activation;
4. while that physical fence is held, validate zero old work/sessions and
   durably publish an activation record containing the qualified deployment,
   exact binding/generation, monotonically new protocol epoch,
   `plan_admission_lifetime_v1`, and digest of the operator fence evidence;
5. permit new runtime open only with replacement access authority plus exact
   agreement with that durable record and coordinator epoch; the first such
   open atomically changes `ACTIVE_UNUSED` to `ACTIVE`, then the operator may
   release the maintenance boundary.

Legal activation edges are:

```text
UNACTIVATED -> ACTIVATING
ACTIVATING -> UNACTIVATED                 (authoritative pre-change/no-effect refusal)
ACTIVATING -> ACTIVE_UNUSED(epoch)         (physical fence and record complete)
ACTIVATING -> ACTIVATION_INDETERMINATE
ACTIVATION_INDETERMINATE -> UNACTIVATED   (authoritative no-activation proof and restored old access)
ACTIVATION_INDETERMINATE -> ACTIVE_UNUSED(epoch)  (authoritative completion)
ACTIVE_UNUSED(epoch) -> UNACTIVATED       (record unused; withdraw under same physical fence and restore old access)
ACTIVE_UNUSED(epoch) -> ACTIVE(epoch)      (first lifetime runtime open)
```

The authority proof is the operator-controlled stop plus physical database/
file exclusion; the durable record makes that completed fact discoverable but
does not create the fence. If the finite wait times out or absence/exclusion
proof fails before access is changed, activation returns a typed no-effect
refusal, returns to `UNACTIVATED` and may resume the legacy deployment. If a
timeout or failure occurs after legacy access is fenced
but before the activation record is authoritatively published, state becomes
`ACTIVATION_INDETERMINATE`: both legacy and lifetime execution remain stopped
until operator recovery either proves no durable activation and restores the
old access, or completes activation. An `ACTIVE_UNUSED` record may be withdrawn
only while the same physical fence proves that no lifetime runtime ever opened.
After the first lifetime open publishes `ACTIVE(epoch)`, rollback to legacy is
forbidden and `ACTIVE(epoch)` has no outgoing activation-state transition.
Recovery must preserve and enforce that exact epoch. Old credentials/sessions/processes
cannot reopen or continue, regardless of whether they understand the marker.

The active protocol epoch remains mandatory across ordinary resource close,
full runtime shutdown, restart, A12 migration, migration recovery and binding
non-reuse/retirement. Those controls may refuse binding work but cannot
deactivate the lifetime protocol, delete or reuse its epoch, reset it to
`UNACTIVATED`, or authorize legacy access. An unknown request to retire,
deactivate, reset or erase the active protocol refuses without changing any
activation/binding/resource state, access fence, lease/permit count, owner,
buffer, A7 knowledge or durable evidence.

`ACTIVATION_INDETERMINATE` likewise has only the two edges shown above. It
retains the operator's physical fence and all evidence until authoritative
no-activation restoration returns to `UNACTIVATED`, or authoritative
activation completion reaches `ACTIVE_UNUSED(epoch)`; there is no retirement
shortcut. If neither proof is available, it remains indeterminate and ordinary
work fails closed.

A brand-new deployment may atomically initialize `ACTIVE_UNUSED(epoch)` under the
same exclusive physical boundary before its first runtime opens; its empty
authoritative process/session inventory is evidence, not an omitted check.
Every restart reads and enforces the active epoch before acquiring database
access. A deployment without operator inventory, session/access fencing and
durable control-record authority cannot enable W2. This design specifies the
future protocol shape only; it does not implement tooling, rotate credentials,
touch a service or claim activation has occurred. Its future implementation
belongs to the W3 runtime integration and W4 deployment/backend owners under a
separately authorized execution brief and independent review.

### 8.2 Normal active-generation coordination

The generation fence is keyed by exact `QualifiedDeployment`, not runtime,
process, pool, cache or connection. Every participating runtime and borrowed
connection must first prove `ACTIVE(epoch)`, then join the same deployment
coordinator at open and negotiate `plan_admission_lifetime_v1`; the first open
may instead atomically validate matching `ACTIVE_UNUSED(epoch)` and publish its
transition to `ACTIVE(epoch)` while the physical activation fence remains held.
Each operation holds a coordinator-issued shared
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
participation, activation epoch, current generation or protocol support refuses
open/work. A locally closing participant remains registered until all retained
permits/containment are terminal, even though its local gate rejects new work.

Migration ordering is exact:

1. acquire the finite-wait deployment migration mutex before any runtime or
   registry lock;
2. validate the request, expected old binding/digests/generation, authority,
   effect class and governed accounting while still effect-free;
3. atomically change the coordinator to `DRAINING_OLD`, preventing every
   participant and connection from acquiring a new old-generation operation,
   refresh or delivery permit; notify each local generation gate without
   changing its ordinary resource lifecycle state;
4. while holding the deployment gate, acquire participant registry and
   subscription queue locks in the §4 order and perform one authoritative
   queue barrier: mark every old-generation queue `MIGRATION_INVALIDATING`,
   invalidate each queued envelope once and release its buffer permit once.
   A refresh that was already running but reaches enqueue concurrently observes
   that marker under the same queue lock, refuses/discards its candidate and
   releases its refresh lease without creating a buffer permit. Dequeue that
   won the lock earlier has already atomically exchanged its buffer permit for
   an active delivery lease and therefore remains counted. The
   `MIGRATION_INVALIDATING` marker remains installed throughout the zero-permit
   wait and migration; a no-effect reopen clears it only after publishing the
   new old-generation admission epoch, so a delayed already-leased refresh can
   never enqueue behind the barrier;
5. wait within the migration-lock deadline until the coordinator proves zero
   old-generation execution and delivery permits across all participants;
6. if the count does not reach zero, refuse before any migration effect,
   release the exclusive request and reopen the same old generation only with
   authoritative no-effect proof and a new admission epoch; invalidated old
   buffers remain invalid and subscriptions refetch rather than resurrect them;
7. acquire the exclusive generation permit and change to `MIGRATING`;
8. perform only the A12-classified migration: metadata proof with no bound
   data/shape change, or atomically governed/accounted DML/DDL effects;
9. durably publish the exact requested next binding, generation and its
   ledger/revision boundary while holding the exclusive permit;
10. retire old handles and durable subscription registrations, clear already-
    invalid queue entries without another permit release, change to `CURRENT`
    carrying the requested next binding, then release the exclusive permit so
    next-generation shared acquisitions may begin.

No migration effect, DDL or backfill occurs before step 8, and no generation
publication or next-generation plan admission occurs before steps 9–10.
Online/mixed-version schema operation is
not added. If failure occurs before step 8, it is a typed no-effect refusal and
may reopen old generation as stated. Failure during or after step 8 is
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
atomically invalidates the envelope and releases it. Migration uses only §8.2
step 4's queue barrier: it stops new refresh permits, marks the queue against
late enqueue, invalidates each still-queued old-generation envelope and
releases each permit exactly once, then waits for active delivery leases to
finish or quiesce before effects.

Delivery lease acquisition validates every envelope field against the current
subscription registration and generation. The publication barrier repeats the
A11 post-await check and generation/lease check. An old-generation, stale-plan,
copied, already-delivered or mismatched buffer is never relabeled; it is
discarded and terminates with typed `RefetchRequired`/generation mismatch.
Duplicate completion for the exact delivery identity is idempotent; a second
handoff or conflicting cursor completion refuses.

The durable registration is also generation-bound. Exclusive migration
cutover retires the old registration atomically with old handles; queued
buffers were already invalidated by the unique pre-zero barrier and cleanup
must not release them again. A still-open idle subscription therefore performs
the A6 refetch and registration handshake in the new generation before another
refresh; it never silently carries its old cursor or registration forward.

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
   hard fences, local resource hierarchy/attribution, subscription unit leases
   and deployment-generation permit;
5. amended execute, snapshot, subscribe, refresh, iterator-delivery,
   migration, pool/connection close and containment handshakes;
6. exact refusal codes for admission required, stale/released/copied/cross-
   runtime/cross-binding/cross-generation lease, lease owner conflict,
   operation outcome conflict, local drain/fence, generation and refetch cases;
7. the issuer-private exact-command/effect worker authorization in §5.1 as an
   explicit A11 extension, while leaving public `TrustedContext` task-bound.

Integration remains future W3/W4/W5 ownership, not W2 document authority:

1. add and accept the W1 result/lifetime protocol and A11 worker-authority
   amendment;
2. implement the deployment coordinator, local resource hierarchy, registry,
   lease state machine and
   containment before enabling plan execution;
3. implement and independently review the operator-owned activation protocol,
   including authoritative inventory and physical legacy-access fencing;
4. activate each existing deployment under the finite stop-the-world procedure
   and durably publish `ACTIVE_UNUSED(epoch)`; the first lifetime open publishes
   `ACTIVE(epoch)`. A new deployment initializes the unused state before first
   open;
5. construct every backend/pool/connection with the exact bound verifier and
   generation coordinator; require `plan_admission_lifetime_v1` at open;
6. change execute/snapshot/subscribe/refresh/delivery and every child/total
   continuation to lease-only guarded calls;
7. make all legacy bare-plan, point-verifier, raw-plan, old-handshake and mixed-
   version paths refuse before lowering or I/O;
8. prove exhaustive consumer/data-flow checks, deployment-wide migration
   fencing and lifecycle vectors before removing old paths or enabling W2.

No stage permits a working legacy path beside reliance on lifetime admission.
Raw `Plan`, the stopped point-in-time verifier result, `plan_admission_v1`
without the lifetime capability, unknown/missing protocol versions and peers
that cannot join the deployment fence all fail closed. For an already-open
legacy peer, this guarantee comes from §8.1's operator stop and physical access
fence, not from expecting that peer to read a marker or negotiate. Backend/compiler import
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
| worker authority before/after enqueue/dequeue/effect | public context stays with issuing task; exact issuer-private command/effect authorization succeeds only while original record, lease, command, worker, generation and ordinal are live |
| context expiry/invalidation while command waits | immediate worker check makes zero adapter calls and revokes unused ordinals |
| non-killable SQLite worker past deadline | hard-fenced `NONQUIESCENT`, exact operation retained; current call may finish privately, but no new command, publication or late commit request |
| read with no transaction identity | still prevents `CLOSED`/migration through its operation identity |
| A7 commit-requested write | lease and commit fence both retained; neither invents the other's proof |
| close one connection/pool/runtime among two runtimes | selected ancestry drains; peer continues acquiring under deployment `CURRENT`; retained local containment remains globally counted |
| cross-runtime migration with two pools/connections | only migration enters `DRAINING_OLD`; exclusive fence waits for both deployment-wide permit sets, not one cache |
| stale/cross-runtime/cross-binding/cross-generation handle | acquisition refuses without a lease |
| copied/fabricated/released lease | every step refuses before lowering/I/O/publication |
| duplicate identical completion | idempotent, counts released once |
| conflicting completion or wrong owner | refuses and preserves original state/counts |
| exception before dispatch | terminal refusal and release |
| exception/cancellation after dispatch | containment until authoritative worker quiescence |
| initial snapshot race | rows, cursor and registration share one generation or whole unit refetches |
| queued buffer plus migration | unique pre-zero barrier stops refresh acquisition, invalidates/releases buffer once, then waits; post-cutover cleanup does not release twice |
| refresh reaches enqueue concurrently with migration barrier | enqueue sees `MIGRATION_INVALIDATING`, creates no buffer permit and releases its refresh lease |
| active delayed delivery across migration | dequeue winner remains an active delivery lease and delays cutover; it is never relabeled after cutover |
| idle subscription | holds no execution permit; close/migration progresses |
| already-open legacy process during activation | lifetime execution/migration refuses until operator inventory plus physical database/file fencing proves it unable to work and `ACTIVE_UNUSED(epoch)` is durably published; first open makes it `ACTIVE` |
| activation restart/rollback | pre-fence failure may resume legacy; post-fence uncertainty stops both; unused activation may withdraw only under the physical fence; post-first-open `ACTIVE` cannot roll back to legacy |
| protocol retirement/deactivation request while active work, buffers, non-killable workers or A7 unknown knowledge exist | request is unsupported and refuses atomically; `ACTIVE(epoch)`, every access fence, owner, count and evidence remain unchanged, and restart still requires the same epoch |
| resource close, migration, binding non-reuse and restart after activation | activation remains the same `ACTIVE(epoch)`; none supplies a protocol reset, epoch erasure/reuse or legacy rollback path |
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
participants for one qualified deployment, close each resource level in one
participant while the other succeeds, then migrate while retained local
containment remains. Worker tests retain a genuinely blocked non-killable
command and pause the issuer-private authority handshake before enqueue, after
enqueue, after dequeue and immediately before effect under success, expiry,
host invalidation, wrong worker, cancellation and reuse. Subscription tests
delay before and after await, race refresh enqueue against the unique migration
queue barrier, check single permit release, invalidate authority,
overflow/refetch and migrate. Activation tests begin with an already-open
legacy peer and require finite refusal until authoritative supervisor plus
database/file access fencing is proven; a marker or new-peer census alone must
fail. Activation-state tests enumerate the exact closed edge set, inject unknown
retire/deactivate/reset requests with active and quiescent deployments, and
require identical pre/post state, access authority, counts and evidence. They
also carry the same `ACTIVE(epoch)` through local/full close, restart,
migration, migration recovery and binding non-reuse.

Syntax-aware architecture checks enumerate every function that reaches plan
lowering, adapter invocation, fetch, assembly, snapshot registration, cursor
advance or public publication. They fail on raw-plan types/returns/caches,
point-only resolution, unleased continuations, missing publication barriers,
lock-order inversions, operation removal before terminal state, local close
mutating deployment state, local-only migration counts, duplicate buffer
release, enqueue after the invalidation barrier, task-context transfer to a
worker, activation based only on cooperative handshakes/markers, or a close
outcome unable to name nontransaction work. They also fail if any protocol
retirement/deactivation/reset API, edge, epoch deletion/reuse path or legacy
rollback from `ACTIVE` exists.

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
Deployment decommissioning is not part of this release or this admission
design; it requires separate future authority and design and cannot be inferred
from binding retirement or resource close.

This design does not modify W1, source, tests, ADRs or grammar; run a build or
database; prove worker/database behavior; accept itself; close the stopped
object; launch an amendment or implementation; or authorize Git/GWZ work. Its
next action is manager pinning and fresh numbered independent Consistency/
Safety review, with the prior originating replacement Safety reviewer verifying
the removed-retirement counterexample and the originating stopped Safety
reviewer retaining the original lifetime closure. This is replacement
remediation round 2 of 2; no third architectural correction is authorized.
GO/GO plus required originating closure can accept only the exact base-plus-
overlay design tuple. A separately authorized W1/A11 amendment,
activation ownership package and implementation execution brief remain
prerequisites.
