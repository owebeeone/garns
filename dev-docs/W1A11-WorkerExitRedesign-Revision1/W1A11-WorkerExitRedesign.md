# GARNs W1/A11 worker-exit replacement design

**Status:** operator-authorized design candidate for independent Consistency/
Safety review; not accepted and not implementation authority  
**Date:** 2026-10-04  
**Scope:** one additive internal ownership redesign for worker exit and the four
bounded stopped-object residuals

## 1. Decision, authority and precedence

This design is the successor object authorized by
`W1A11-WorkerExitRedesign-Brief.md` at SHA-256
`9ba4854b5ce14c86b22b76f1b1a42c05acef228723aa427999c7a5123b1f6a56`.
It is based on the accepted composed W2 pair:

- `W2-QueryPlanningDesign.md` at
  `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`;
- `W2-AdmissionLifetimeRedesign.md` at
  `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`.

It does not accept or amend the stopped 71-file source candidate. That source
remains evidence at `W1A11-ContractAmendment-MANIFEST-3.sha256`, whose SHA-256
is `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
The stopped amendment's two architecture corrections remain exhausted. This
new object's correction count starts at zero only because the operator
explicitly authorized the replacement design.

The design makes one decision, not a menu: the runtime lifetime registry is the
sole mutation owner for a lease, its worker authorization, effect reservation,
exit, containment, result acceptance and terminal release. Worker authority is
not a second independently mutable registry. Deployment generation remains the
coordinator's separate ownership domain and is composed with the lifetime
registry only through the established lock order and sealed permits.

The following accepted truths are unchanged:

- `Plan` is never an executable argument, result, cache value or unwrap. Exact
  admitted handles, operation leases and issuer-owned closed consumers remain
  the only execution seam.
- Result roles and all five accepted result vectors remain unchanged.
- Parameters, binding, generation, resource ancestry and operation kind remain
  pinned at acquisition. Child, nested and total commands remain derived,
  parent-owned and covered by the parent's one generation permit.
- Public `TrustedContext` remains an empty exact-instance identity valid only
  in its original runtime task. No worker, result receipt or containment record
  carries or transfers claims.
- A7 transaction knowledge remains exactly `KNOWN_ABORTED`,
  `KNOWN_COMMITTED` or `INDETERMINATE`. Worker quiescence, operation terminal
  state and transaction knowledge are independent facts.
- Local close remains distinct from deployment drain. The active lifetime
  protocol has no reset, deactivation or retirement edge.

## 2. Exact additive supersession

Only the following clauses are refined. Every other accepted W2 base/overlay
clause, A1--A16 requirement and stopped amendment result-role/no-raw-Plan claim
is retained.

| Controlling clause or candidate claim | Exact additive disposition |
|---|---|
| Accepted overlay §4: “Worker-to-runtime result handoff and worker-to-containment transfer are likewise compare-and-transfer operations naming the expected current owner.” | Completed by §§3--7 below: exact command-exit states, bound receiving runtime task, issuer-owned containment identity, stop observation, replay/conflict rules and publication ordering. |
| Accepted overlay §5.1: dispatch binds a command/worker/authorization and each ordinal is consumed immediately before effect. | Strengthened: one registry transaction reserves an ordinal and marks an effect in flight before invocation; nested/reentrant reservation refuses; any raised `BaseException` or running cancellation transfers to containment and revokes every unused ordinal before another effect can begin. |
| Accepted overlay §§6--7: hard fencing retains contained work until authoritative quiescence and close distinguishes operations from A7 identities. | Refined with an authoritative executor-issued command-stop observation. A worker return, exception, cancellation, `finally` or cleanup callback is not quiescence. Success is not acceptable or publishable before stop observation. |
| Accepted overlay §8.2: a runtime joins the coordinator at open and a locally closing participant remains registered until retained containment is terminal. | Completed by §9's activation-bracketed sealed membership and exact join/leave grammar. Construction before activation creates no member or admission authority; quiescent final close removes the member from future attempts. |
| Accepted overlay §9: only a caller-visible handoff advances delivery; a neutral refresh advances internal cursor without a batch. | Completed by §§8 and 10. This design selects registration retirement/refetch after an unpublished head failure and defines an ordered changed/neutral lineage so neutral progress cannot overtake queued or active delivery. |
| Accepted overlay §8.2 step 6 and the stopped amendment's “exact current attempt” no-effect claim. | Strengthened by §11: proof binds current attempt phase, monotonically increasing phase serial and the exact request identity/requested successor applicable to that phase. |
| Stopped amendment claim that worker validation/ordinal consumption before an effect callback represents the private worker seam. | Replaced in worker-exit scope only. Arbitrary effect callbacks are not an executable contract seam; production uses issuer-owned closed effect commands. A deterministic reference fixture may install a fixed hostile action at trusted setup to exercise exceptions/reentrancy, but callers cannot supply it per invocation. |
| Stopped amendment claim that produced/delivered frontiers plus one active FIFO head represent buffering. | Refined with outcome-sensitive head settlement, registration retirement and the ordered zero-permit neutral lineage. Successful existing FIFO cases remain required. |

This document does not supersede the original A7 commit grammar, public
context ownership, accepted activation physical-fence requirements, migration
effect accounting, or any result/provenance contract.

## 3. Ownership, identities and trust

All names are internal and provisional pending W3 Surface review. The future
contract uses empty sealed exact-instance identities:

```text
WorkerCommandAuthorization   # existing private command authority
WorkerEffectReservation      # one reserved ordinal; never caller-created
WorkerExitReceipt            # one success/failure/cancel exit record
WorkerStopReceipt            # executor-issued command-stack quiescence
RuntimeContinuationOwner     # issuer-private result receiver identity
WorkerContainmentOwner       # issuer-private failure/cancel owner identity
ParticipantMembership        # coordinator-issued runtime membership
MigrationRequestIdentity     # coordinator-issued phase-specific request
MigrationNoEffectProof       # existing name, strengthened private record
NeutralRefreshReceipt        # exact committed neutral outcome
```

They are exact-type, identity-compared, immutable, empty, noncopyable and
nonserializable. Their representations expose no runtime, task, context,
claims, plan, lease, command, worker, binding, cursor, result or error. Private
records, not handles, hold those values.

One private lifetime record owns this complete tuple:

```text
(runtime identity, operation identity, exact lease, admitted record,
 immutable resource ancestry, generation permit, original context record,
 receiving runtime task, RuntimeContinuationOwner,
 exact closed command, assigned executor worker,
 WorkerCommandAuthorization, ordered effect schedule,
 active WorkerEffectReservation or none, completed/unused ordinals,
 command-exit phase and exit serial, result or failure record,
 WorkerContainmentOwner, stop-observed bit, publication/completion record)
```

The receiving task and assigned worker are captured from trusted injected
providers. They are never method arguments supplied by an ordinary caller.
At dispatch the authority issuer proves that the current task owns the
original context and privately records that task as the sole receiver. At
dequeue, effect reservation and worker exit, the injected current-worker
provider must report the exact assigned worker. At result acceptance, the
injected current-task provider must report the exact recorded receiving task
and A11 validates the original context at zero staleness. Nothing rebinds the
context to the worker.

`WorkerContainmentOwner` is allocated by the registry at operation creation
and never leaves it. A caller, worker or cleanup callback cannot nominate a
containment owner. The registry is the authoritative quiescence owner: only an
exact `WorkerStopReceipt` issued by its bound executor after the command stack
and all trusted cleanup have exited can establish command quiescence.

## 4. Closed worker-command and effect grammar

### 4.1 Command states

The issuer-private command state is exactly:

```text
QUEUED
RUNNING_IDLE
EFFECT_IN_FLIGHT(ordinal, reservation)
SUCCESS_PENDING(exit_receipt, result_identity)
CONTAINED(exit_receipt, reason, effect_knowledge)
QUIESCENT_SUCCESS(exit_receipt, result_identity)
QUIESCENT_CONTAINED(exit_receipt, reason, effect_knowledge)
RESULT_ACCEPTED(exit_receipt)
```

`effect_knowledge` is exactly `NOT_BEGUN`, `RETURNED`, or
`BEGUN_UNCERTAIN`. `NOT_BEGUN` means no effect ordinal was ever reserved;
`RETURNED` means at least one was reserved and every reserved effect returned
before containment; `BEGUN_UNCERTAIN` means an effect was reserved but had not
authoritatively returned when containment won. These are worker-command facts
only and never manufacture A7 database knowledge. The legal edges are:

```text
QUEUED -> RUNNING_IDLE                         authoritative dequeue
QUEUED -> terminal CANCELLED_CONFIRMED         authoritative queue removal
RUNNING_IDLE -> EFFECT_IN_FLIGHT               exact ordinal reservation
EFFECT_IN_FLIGHT -> RUNNING_IDLE               fixed effect returned
RUNNING_IDLE -> SUCCESS_PENDING                successful command exit
RUNNING_IDLE|EFFECT_IN_FLIGHT -> CONTAINED     cancel/fence/failure
SUCCESS_PENDING -> CONTAINED                   cancel/fence before stop
SUCCESS_PENDING -> QUIESCENT_SUCCESS           exact stop observation
CONTAINED -> QUIESCENT_CONTAINED               exact stop observation
QUIESCENT_SUCCESS -> QUIESCENT_CONTAINED       fence before result accept
QUIESCENT_SUCCESS -> RESULT_ACCEPTED           exact receiving-task accept
```

There is no success edge out of `CONTAINED`, no result-accept edge before
quiescence, and no edge back to a worker-owned state. A late worker return
after containment is recorded only as a closed diagnostic on that containment
record; it cannot expose a result, change effect knowledge, restore ordinals,
publish or change terminal outcome.

The lease's existing state remains the outer grammar. `QUEUED` maps to lease
`QUEUED`; running states map to lease `RUNNING`; containment states map to
lease `CONTAINED`. `RESULT_ACCEPTED` returns ownership to the exact runtime
continuation and the lease remains `RUNNING` for assembly/publication or a
later separately authorized command. Terminal `SUCCEEDED`, `REFUSED` and
`CANCELLED_CONFIRMED` remain lease outcomes, not worker-exit states.

### 4.2 Effect reservation and nonreentrancy

Dispatch binds an issuer-owned finite ordered `WorkerEffectSchedule`. Each
ordinal is classified privately as required or optional and names one exact
closed effect command. The runtime, not a caller, constructs that schedule.
Successful command exit requires every required ordinal to have returned; it
atomically revokes any unused optional ordinal.

The worker wrapper's internal operations are conceptually:

```text
dispatch_worker(lease, closed_command, effect_schedule)
  -> WorkerCommandAuthorization
run_effect(authorization, ordinal) -> ClosedWorkerEffectResult
worker_exit_success(authorization, closed_result) -> WorkerExitReceipt
worker_exit_failure(authorization, closed_failure) -> WorkerExitReceipt
request_worker_cancel(lease) -> cancellation disposition
observe_worker_stopped(stop_receipt) -> None
accept_worker_result(exit_receipt) -> ClosedWorkerResult
```

These are issuer-private calls. They take no caller-provided worker identity,
task identity, claims, clock, epoch, binding or containment owner.

`run_effect` first performs one atomic validate-and-reserve mutation under the
lifetime registry owner:

1. require the exact live runtime/operation/lease/command/authorization tuple,
   command state `RUNNING_IDLE`, exact current assigned worker, current
   original context record, binding/generation, local fences and next legal
   ordinal;
2. reject if any effect reservation is active or the wrapper is already on
   this command's stack;
3. consume the ordinal, create the exact reservation and set
   `EFFECT_IN_FLIGHT` before invoking the fixed effect;
4. look up that ordinal's issuer-owned closed effect in the immutable schedule
   and invoke it outside the state lock; no per-call effect argument, user
   callback or plan-holding frame runs inside the mutation boundary;
5. on normal return, atomically bind the closed effect result and restore
   `RUNNING_IDLE`;
6. on any `BaseException`, including task cancellation, atomically revoke all
   unused ordinals, set `CONTAINED`, transfer lease ownership from the worker
   to the pre-existing containment owner and retain the generation charge,
   then re-raise the original exception after state is safe.

An effect reserved before a concurrent cancel may still begin; it is already a
begun/uncertain effect. Cancellation revokes every *other* unused ordinal and
contains the command before any other effect can reserve. A same-worker nested
call, a callback-induced reentrant call and a concurrent call all observe the
active reservation and refuse without consuming an ordinal or changing owner,
state or counts.

## 5. Worker success, failure and cancellation exit

### 5.1 Success

The outermost trusted worker wrapper performs every trusted cleanup before it
requests success exit. `worker_exit_success` requires `RUNNING_IDLE`, no active
reservation, every required ordinal returned, a closed issuer-owned result and
the exact current worker. In one mutation it revokes optional unused ordinals,
creates one `WorkerExitReceipt`, records `SUCCESS_PENDING`, transfers the
lease owner from worker to registry-held pending-result escrow and closes the
authorization. It does not publish, release a permit or expose the result.

The bound executor then issues `WorkerStopReceipt` only after the command
frame cannot resume. Exact stop observation changes `SUCCESS_PENDING` to
`QUIESCENT_SUCCESS`. The receiving runtime task calls `accept_worker_result`.
That call succeeds only if the current task is the privately recorded receiver,
the original context validates for the pinned capability/scope, the result and
exit receipt are exact and live, and lease/admission/resource/generation
barriers remain current. It changes ownership to the runtime continuation and
returns closed result data. Wrong task or wrong tuple refuses mutation-free;
expiry, invalidation or a hard fence closes the result and transfers to
containment because it can never legally publish.

### 5.2 Failure and cancellation

An effect exception is contained by the `run_effect` wrapper before the
exception leaves it and creates the failure exit receipt with
`BEGUN_UNCERTAIN`. The outer wrapper's observation of that same exact receipt
is a replay, not a second exit. A failure outside an active effect is contained
by `worker_exit_failure`: it records `NOT_BEGUN` only if no ordinal was ever
reserved and otherwise records `RETURNED`. The first failure or cancel exit
record is primary. A racing different exit kind and later cleanup failures are
appended as bounded closed diagnostics and never overwrite primary effect
knowledge or A7 truth.

Cancellation has only two trusted sources: a request by the exact recorded
receiving task while its original context is live, or an issuer-internal
runtime fence/expiry/close event. The task and source are obtained from trusted
providers; no caller supplies an owner or claims proof. Queued cancellation
takes the queue lock and either removes the exact command, revokes its
authorization and completes `CANCELLED_CONFIRMED` exactly once, or loses to
dequeue. After dequeue, cancellation atomically creates a cancel exit receipt,
records `cancel_requested`, revokes unused ordinals and transfers ownership to
containment. It records `NOT_BEGUN` if no ordinal was reserved, `RETURNED` if
all prior reservations returned, and `BEGUN_UNCERTAIN` if a reservation is
active. This receipt creation applies while the worker still owns
`RUNNING_IDLE` or `EFFECT_IN_FLIGHT`; the post-success case below retains the
already committed success receipt. Cancellation cannot release the permit
until stop observation.

Hard fence and context invalidation use the same containment grammar. A
worker cannot complete or publish after that edge. The former caller/runtime
task also cannot complete a contained lease. Only the registry containment
owner may terminalize it after exact stop observation.

If cancellation, context invalidation or a hard fence wins after creation of a
success receipt but before result acceptance, the mutation closes the private
result and moves `SUCCESS_PENDING` to `CONTAINED`, or already-quiescent
`QUIESCENT_SUCCESS` to `QUIESCENT_CONTAINED`. It retains the success receipt as
a tombstone but cannot accept or publish it. A fence before stop still waits
for the exact stop receipt; a fence after stop is already quiescent. Once
`RESULT_ACCEPTED`, command ownership is finished; a later assembly/publication
failure follows the outer lease's ordinary containment grammar and cannot
reopen the command.

### 5.3 Cleanup failure schedule

The required wrapper sequence is:

```text
capture command-body outcome; a fixed-effect BaseException is already contained
run trusted cleanup outside the state lock
  cleanup BaseException -> atomically contain or append to prior containment
if body and cleanup succeeded -> request success exit
else -> preserve the first BaseException and its exact failure/cancel receipt
return or rethrow; only after the command frame exits may executor issue stop
```

Success exit is requested only after cleanup returns. Therefore cleanup cannot
fail after a publishable success receipt exists. If cleanup raises after a
result was privately computed, that result is closed and discarded and the
command follows failure containment. A failure while recording cleanup cannot
invoke application code; validation completes before mutation and every
rejected record preserves the existing primary state.

## 6. Idempotency, conflicts and authoritative completion

Every exit has one monotonically unique command-local `exit_serial`. Repeating
the same operation with the same exact authorization, exit receipt, kind,
closed result/failure digest and serial is idempotent. Repeating stop
observation is idempotent. A different kind, result, failure, serial, lease,
command, authorization, worker, receiver, runtime, binding or generation is an
outcome conflict and changes nothing.

Closing an authorization retains an immutable private exit tombstone until
the operation is terminal. Exact success, failure or cancel replay is answered
from that tombstone even though the live authorization can no longer reserve
an effect. A failure/cancel race is therefore first-commit-wins: the loser is
only a bounded diagnostic, cannot replace the receipt or effect knowledge, and
cannot cause a second owner transfer or permit release.

The following never release a generation permit: worker return, success
receipt creation, failure receipt creation, cancellation request, result
acceptance or stop observation by itself. After successful acceptance, the
runtime may continue guarded assembly and reach the normal publication
barrier. That barrier atomically records publication and terminal
`SUCCEEDED`, releases ancestry charges and the shared permit exactly once, and
only then makes the closed value available to the caller-owned future/channel.
There is no callback between commit and exposure. A repeated publication is
idempotent only for the same committed receipt; a conflicting completion
refuses. A task cancelled before that commit observes no publication.

For contained work, stop observation establishes operation quiescence, not
database outcome. The containment owner may then complete the operation as
`REFUSED` or, only for an authoritatively not-started cancellation, as
`CANCELLED_CONFIRMED`, releasing the operation permit once. Any A7 transaction
identity remains independently retained until its accepted terminal evidence.
Consequently:

- live operation, with zero or more A7 identities -> `NONQUIESCENT`;
- no live operation but unresolved A7 identities -> `UNRESOLVED`;
- neither -> `CLOSED`.

A known commit does not establish worker quiescence. Worker quiescence does not
establish abort, commit or permission to retry. The existing A7 late-commit
fence remains controlling.

## 7. Mandatory worker-exit interleavings

The future reference regressions must instrument a pause at queue insertion,
dequeue, ordinal reservation, immediately before fixed effect invocation,
during the effect, effect return, cleanup, success-exit commit, stop
observation, result acceptance and final publication.

| Trace | Required terminal observation |
|---|---|
| Wrong lease/command/authorization/runtime/generation/current worker at dequeue, effect or exit | refusal before mutation; no effect, ordinal consumption, owner transfer or count change. |
| Effect 1 raises while effect 2 is unused | before the exception escapes, lease is containment-owned, effect 2 is revoked, count remains charged; effect 2 and result exit refuse. |
| Effect attempts nested/reentrant `run_effect` | active reservation makes the nested attempt refuse; outer effect has the sole reservation and the nested attempt consumes nothing. |
| Cancellation loses dequeue race | unused ordinals revoke, running command becomes containment-owned; it stays `NONQUIESCENT` until stop observation. |
| Cancellation between reservation and invocation | reserved effect may begin and is `BEGUN_UNCERTAIN`; no other effect may begin and no result may publish. |
| Local close, context revocation or generation drain races dequeue/reservation/effect/exit | barrier-first refuses before reservation; reservation-first transfers to containment with the charge retained through stop; success-exit-first still cannot cross accept/publication revalidation. Old-generation drain cannot complete from the receipt alone. |
| Cleanup callback raises after a private result was computed | result is discarded; cleanup failure is secondary; containment and counts survive until stop observation. |
| Worker success while receiving runtime task is wrong/child task | receipt remains private and unaccepted; no claims transfer and no publication. Exact original receiving task may accept only while original context/barriers remain valid. |
| Context expires or runtime hard-fences between success exit and accept | result closes, transition is containment, no publication; stop/quiescence and A7 truth remain independently retained. |
| Success/failure/cancel exit replay | exact replay is idempotent; conflicting replay refuses with one owner, one result and one charge. |
| Late success after failure/cancel containment | closed diagnostic only; no owner, result, terminal state, ordinal or cursor changes. |
| Publication return path raises/cancels before commit | no outward value and no success. After the atomic commit, delivery to the caller-owned future is the publication fact and cannot be relabeled. |

## 8. Failed FIFO delivery: registration retirement/refetch

This design selects one fail-closed rule: an exact FIFO head that does not
commit caller-visible publication retires its registration and requires a new
A6 refetch/registration handshake. It is never requeued and successors never
cross it.

A registration has exact states `ACTIVE`, `RETIRING_REFETCH` and `RETIRED`.
An active handoff records one exact head and one publication-commit bit.
Its only internal settlement calls are:

```text
settle_delivery_success(handoff_lease, exact_publication_receipt)
  -> delivery settlement
settle_delivery_non_success(handoff_lease, exact_terminal_outcome)
  -> RefetchRequired
```

Both outcome arguments are registry-issued closed records, never booleans or
caller-selected labels. The same lifetime-registry mutation owns buffer,
handoff, operation and generation count changes.

Successful settlement requires that exact bit, terminal `SUCCEEDED`, exact
owner/lease/envelope and current FIFO head. In one mutation it advances
`delivered_through`, removes the head, releases the handoff operation permit
and drains any newly eligible neutral prefix described in §10.

Any legal non-success before publication atomically:

1. leaves `delivered_through` unchanged;
2. marks the head failed and the registration `RETIRING_REFETCH`;
3. invalidates every queued successor and releases each queued buffer permit
   exactly once;
4. prevents new refresh, enqueue, dequeue and handoff on that registration;
5. retains the active handoff's operation permit until worker/iterator
   quiescence, then releases it once and records `RETIRED`;
6. makes every later use return typed `RefetchRequired`, from which a new
   snapshot creates a new registration and cursor lineage.

Produced progress and diagnostic lineage may be retained, but neither is
reported as delivered. Exact repeated failure settlement is idempotent;
success after retirement and failure after committed publication are conflicts.
Close and migration use the same retirement mutation, do not double-release
queued permits, and continue waiting for an active contained handoff.

Refetch never resumes from the retired registration's produced cursor. It
performs A6's complete snapshot/high-water/registration handshake under a new
lease. Only atomic caller-visible publication of that complete snapshot makes
its high-water the new registration's produced and delivered baseline. Refusal
leaves no usable new registration. Thus retirement cannot hide the failed gap,
and a later changed range is relative to a published complete baseline rather
than the abandoned lineage.

This is the prospective design disposition for `ReviewCode-3 P2-1`,
`ReviewState-3 P2-2` and
`FreshCodeClosure-2 P2-1`, retaining the `ReviewCode-2 P2-2` and
`ReviewState-2 P2-1` obligations. The mandatory causal regression queues
`(0,1]` and `(1,2]`, fails the first before publication under direct refusal,
authority expiry, local fence, cancellation and cleanup failure, and proves:
delivery stays at 0, the second cannot dequeue, queued permits release once,
the active charge persists to quiescence, repeated settlement changes nothing,
and only a new refetch registration can resume. Existing two-head successful
FIFO and duplicate-success tests remain mandatory.

## 9. Activation-bracketed participant lifecycle

Participant membership is not a constructor side effect. A registry may be
constructed while unactivated only in `UNJOINED`, with no coordinator member,
admitted handle or executable authority. The exact membership states are:

```text
UNJOINED -> JOINED
UNJOINED -> LEFT
JOINED -> LEAVE_PENDING -> LEFT
JOINED -> LEFT
```

`join_runtime` is a coordinator mutation performed atomically with an exact
lifetime-capable open. It validates `ACTIVE_UNUSED(epoch)`/first-open or
`ACTIVE(epoch)`, the exact binding, protocol epoch, runtime identity and local
open resource, then issues `ParticipantMembership`. First open changes
`ACTIVE_UNUSED` to `ACTIVE` in the same transaction. Admission records and
leases bind the exact membership and join serial. Pre-join admission refuses;
no preactivation handle can become valid after activation.

The internal call shapes are exact:

```text
join_runtime(exact_lifetime_open_record) -> ParticipantMembership
request_leave(ParticipantMembership) -> LEAVE_PENDING|LEFT
finalize_leave(ParticipantMembership) -> LEFT
close_unjoined(exact_lifetime_open_record) -> LEFT
```

Runtime, coordinator, binding and epoch come from the private records and
trusted providers, not additional arguments.

Closing before activation performs only `UNJOINED -> LEFT` after local
construction resources are closed. It creates, removes and acknowledges no
coordinator membership, and later open/join on that registry refuses. This is
the complete leave-before-activation behavior.

`request_leave` requires local runtime drain/fence and rejects new acquisition.
`finalize_leave` removes the exact membership from future topology only when
the runtime is `LOCAL_CLOSED` and has no operation/generation permit, queued or
active delivery, worker/containment record, registration-close work or
unresolved close obligation, including A7 identities. Duplicate, copied,
stale-epoch, wrong-runtime and cross-coordinator tokens refuse without loss of
membership.

`begin_drain` freezes exact `ParticipantMembership` identities. Join during an
attempt refuses. A member requested to leave during an attempt becomes
`LEAVE_PENDING`, remains in that attempt's required set and must install and
acknowledge its barrier. The attempt set never mutates. After successful
cutover, no-effect reopen or recovery closes the attempt, an open member is
rebased to the resulting current binding while all old admissions remain
invalid, and a quiescent `LEAVE_PENDING` member becomes `LEFT`. A member closed
after migration follows the same final leave. An idle runtime that has reached
`LEFT` is absent from every later attempt and can never become a permanent
acknowledgement obligation.

This is the prospective design disposition for `ReviewCode-3 P2-2`.
Regressions cover construction/admission before
activation; first-open atomic join; leave before activation; leave with each
retained obligation; duplicate/copy/cross/stale tokens; join and leave during
drain; close during migration; successful and no-effect migration; close after
migration; and a later attempt containing exactly the still-joined live
members.

## 10. Neutral refresh lineage

Each registration owns one ordered contiguous lineage in addition to separate
`produced_through` and `delivered_through` cursors. An entry is exactly:

```text
CHANGED(previous, observed_through, envelope, QUEUED|ACTIVE|PUBLISHED|FAILED)
NEUTRAL(previous, observed_through, neutral_receipt, PENDING|ABSORBED)
```

A trusted fixed comparator classifies an exact sealed refresh candidate as
changed or neutral from its frozen prior/current keyed result. An ordinary
caller cannot select the classification. Both commits revalidate the same
candidate, lease, operation, registration, admission, parameters, plan digest,
binding/generation, queue, authority, local state, migration marker and exact
`previous == produced_through` before one atomic mutation.

The sole internal entry is:

```text
commit_refresh(exact_sealed_candidate)
  -> ClosedBatchEnvelope | NeutralRefreshReceipt
```

It invokes the fixed comparator and commits exactly one branch. There are no
separately callable changed/neutral commit methods.

Changed commit advances `produced_through`, appends `CHANGED` and exchanges
the refresh lease for one queued buffer permit as already required. Neutral
commit consumes the candidate once, advances `produced_through`, appends
`NEUTRAL`, creates no batch/envelope/buffer permit, returns one exact
`NeutralRefreshReceipt`, and completes/releases only the refresh lease.

`delivered_through` advances only by folding a contiguous lineage prefix:

- a `CHANGED` entry folds only after exact caller-visible publication commit;
- a `NEUTRAL` entry folds automatically only when it is the lineage head,
  meaning every earlier changed entry has already published;
- folding stops at queued, active or failed changed work.

Here `produced_through` is the input range already classified, while
`delivered_through` is the greatest range through which the caller's published
state is known current. Folding a neutral range advances that semantic
frontier because the state is unchanged; it does not record a delivery,
increment publication count or create a permit. The separate publication
ledger remains the only evidence that a changed value was caller-visible.

Therefore with zero queued ranges, a neutral `(0,1]` independently advances
both cursors to 1 without a delivery. With one or many queued/active ranges,
neutral entries advance only `produced_through` and wait behind them. When the
last prior changed range publishes, the registry absorbs the consecutive
neutral prefix and then the next changed range whose `previous` equals that
frontier becomes eligible. A prior changed failure retires the registration;
pending neutral and changed successors are discarded without inventing
delivery. This neither makes an older envelope look delivered nor strands the
next changed range.

Fabricated, copied, cross-lease, cross-registration, stale-cursor,
wrong-generation, fenced, migration-invalidated and wrong-classification
candidates refuse before candidate consumption, cursor movement or count
change. Replaying the same committed neutral receipt is idempotent with no
movement; attempting changed publication from that consumed candidate is a
conflict. Close/migration retirement discards zero-permit neutral entries and
handles only actual permits once.

This is the prospective design disposition for `ReviewState-3 P2-3`.
Mandatory traces cover zero, one and multiple
queued changed ranges; an active delayed head; neutral-neutral-changed chains;
changed-neutral-changed; earlier head failure; all provenance/barrier attacks;
replay/conflict; and migration/close immediately before neutral commit. Every
trace asserts produced cursor, delivered cursor, lineage order, queue, active
head, permit count, publication count and refetch state.

## 11. Phase- and request-exact no-effect proof

A migration attempt privately records:

```text
(attempt identity, phase, phase_serial, old binding, requested binding or none,
 exact phase request identity, protocol/admission epochs,
 frozen participants/acknowledgements, effect_begun, closed)
```

The phase is exactly `DRAINING_OLD`, `MIGRATING_PRE_EFFECT` or
`EFFECT_BEGUN`. Every phase transition increments a monotonically unique
attempt-local `phase_serial`. Entering `DRAINING_OLD` allocates the exact drain
request identity with no requested successor. Entering
`MIGRATING_PRE_EFFECT` increments the serial, allocates a different
`MigrationRequestIdentity` and binds the exact requested successor. Entering
`EFFECT_BEGUN` increments the serial again and permanently disables no-effect
reopen.

The private `MigrationNoEffectRecord` adds `phase`, `phase_serial`, exact phase
request identity and requested successor (`None` only in `DRAINING_OLD`). A
trusted coordinator release observation is issued only after the request for
that exact phase is released and no effect began; caller-provided strings are
not production proof. The deterministic reference may use named sealed fixture
observations but cannot claim physical/durable proof.

The internal calls are:

```text
observe_request_released(exact_attempt, exact_phase_request)
  -> MigrationNoEffectProof
reopen_no_effect(MigrationNoEffectProof) -> reopen disposition
```

Both resolve coordinator, phase serial, successor and epochs from
issuer-private records; neither accepts caller-supplied substitutes.

`reopen_no_effect` first validates, without mutation, exact coordinator,
attempt, current phase and serial, request identity, old binding, requested
successor, activation/admission epochs, all frozen acknowledgements, no-effect
state and unconsumed proof. Only then does one commit consume the proof,
increment admission epoch, invalidate every old admission and old queued
buffer, release each invalidated buffer permit once, close the attempt and
reopen queues under the new epoch without resurrecting invalid buffers.

A `DRAINING_OLD` proof is valid only while that exact phase/serial/request is
current. `begin_migration` increments the serial and makes every prior proof
stale. A `MIGRATING_PRE_EFFECT` proof must be issued after that transition and
bind the exact requested successor and exclusive request. Replay, wrong
request, wrong successor, cross-coordinator, cross-attempt and prior-phase
proofs refuse with phase, binding, admission epoch, queue markers, membership,
permit counts and evidence unchanged.

This is the prospective design disposition for the residual
`OriginStateClosure-2 State-Closure-P2-1`, retaining
`OriginStateClosure-1 State-Closure-P2-1`. Its mandatory causal trace issues a
DRAINING proof, completes barriers, enters MIGRATING on the same attempt and
proves the old proof refuses mutation-free; a newly issued exact MIGRATING
proof reopens once; replay and wrong-request/successor variants refuse.

## 12. Complete finding and regression disposition

The five stopped roots receive these exact design dispositions; none is called
closed on source because this is design only.

| Root and all stopped IDs | Design disposition | Mandatory later evidence |
|---|---|---|
| Worker exit — `ReviewState-3 P2-1` | §§3--7 define exact success, failure and cancellation transfers, result receipt, stop observation, receiver trust, containment and terminal release. | Deterministic causal traces in §7, syntax-aware transition/owner/ordinal checks, then real async/thread executor tests at W3. |
| Failed FIFO — `ReviewCode-3 P2-1`; `ReviewState-3 P2-2`; `FreshCodeClosure-2 P2-1`, retaining `ReviewCode-2 P2-2`/`ReviewState-2 P2-1` | §8 selects registration retirement/refetch; only committed head publication advances delivery. | Two-range failure/success, every non-success, replay, close and migration traces with exact counts. |
| Participant lifecycle — `ReviewCode-3 P2-2` | §9 makes membership activation-bracketed and leave quiescence-bound without mutating frozen attempts. | Pre/post activation, drain, migration and local-close topology traces. |
| Neutral refresh — `ReviewState-3 P2-3` | §10 adds sealed neutral consumption and ordered zero-permit lineage across queued/active ranges. | Zero/one/multiple range, provenance, barrier, failure and replay traces. |
| Phase proof — `OriginStateClosure-2 State-Closure-P2-1`, retaining `OriginStateClosure-1 State-Closure-P2-1` | §11 binds proof to exact phase serial/request/successor. | Same-attempt cross-phase trace plus exact new-phase success and every replay/cross/wrong variant. |

All earlier successful attacks remain mandatory regressions. The initial 18
IDs are `ReviewCode P2-1` through `P2-9`, `ReviewState P2-1` through `P2-8`,
and `ReviewState-Supplement P2-1`; expanded revocation under State P2-4 remains
explicit. The correction-1 13 IDs are `ReviewCode-2 P2-1` through `P2-3`,
`ReviewState-2 P2-1` through `P2-6`, `OriginCodeClosure-1 P2-1` residual,
`OriginCodeClosure-1 P2-6` residual, `OriginCodeClosure-1 P2-3` bounded route,
and `OriginStateClosure-1 State-Closure-P2-1`. Their F1--F10 causal attacks
remain unchanged except for the stronger F2 and F8 traces above. In particular,
callback-free plan containment, pinned parameters, commit-before-return,
expanded publication revocation, same activation fence, exact permits,
parent-owned derived commands, current-worker authentication, queue-target
barriers and exact-successor generation must all still pass.

State-machine/property tests must enumerate every legal edge above and reject
every other edge. Every refusal asserts unchanged owner, command/lease state,
active reservation, ordinal sets, result/failure record, publication count,
resource/deployment counts, lineage cursors, membership and migration phase.
Fast syntax-aware source checks must enumerate all executable plan consumers,
worker-effect/exit callers, lease terminalizers, membership mutations, cursor
mutations and proof constructors, including disabled platform branches. They
must fail on a raw `Plan` seam, individual conditional declaration attributes,
unbraced C-style control flow where applicable, caller-provided task/worker/
claims proof, independent child permits, or a second mutable worker-exit owner.

## 13. Future implementation ownership and cohesion

This design authorizes no file change. A later execution brief should propose,
not infer, the following cohesive ownership:

| Future path | Cohesive responsibility |
|---|---|
| `src/garns/backends/contracts/admission.py` | Closed outer lease/operation states and provisional protocol signatures only. |
| `src/garns/backends/contracts/worker_authority.py` | Empty worker/effect/exit/stop identity types and validation helpers; no independently mutable authorization table. |
| `src/garns/backends/contracts/lifetime_reference.py` | Sole deterministic mutation owner for lease, authorization, reservation, worker exit, containment, result acceptance, terminal release and cross-ledger atomic ordering. |
| `src/garns/backends/contracts/buffer_reference.py` | Registration lineage and retirement subledger, mutated only inside a lifetime-registry transaction. |
| `src/garns/backends/contracts/snapshot_reference.py` | Sealed changed/neutral candidate records and fixed trusted classification; no database provenance claim. |
| `src/garns/backends/contracts/generation_reference.py` | Sole membership, generation count, attempt phase/request and proof-consumption owner. |
| `src/garns/backends/contracts/migration_reference.py` | Empty migration/membership/request/proof types and private record shapes, not an independent coordinator. |
| `src/garns/backends/contracts/lifetime.py`, `protocols.py`, `values.py` | Shared closed values/refusals and provisional internal seams; no public freeze. |
| `tests/contracts/test_worker_authority.py`, `test_admission_contracts.py`, `test_lifetime_contracts.py`, `test_generation_contracts.py` | All mapped deterministic transitions; a separate `test_worker_exit_contracts.py` is justified only if the later brief assigns it as the focused causal schedule, not to split assertions by line count. |
| `docs/adr/A16-admission-lifetime.md`, `dev-docs/W1A11-ContractAmendment.md` | Additive accepted-decision wording and exact supersession after source review; never rewrite A1--A15. |

The current 796-line `lifetime_reference.py` remains one recorded atomic-state
exception. It must not be split merely to reach a line target: worker exit
touches the same lease owner, generation charge, local ancestry and publication
record, so moving its mutations behind another object would create two owners
and make rollback/interleaving reasoning cyclic. Immutable identity/type
separation is useful but is not a concurrency proof. Revisit a split only when
the actual runtime supplies one transactional state owner whose subledgers can
commit as one operation; at that point mechanical relocation must preserve
attributes and owning scopes and receive its own review.

The deterministic reference implementation will model each transition as one
validate-then-commit step with injected pause points. It does not prove that
Python locks, task cancellation, a worker thread, a process boundary or a
database transaction provides that atomicity. Production implementation must
use the retained lock order: deployment activation/generation gate; local
resource gates from ancestor to descendant; one runtime lifetime-state lock;
bound executor queue; A7 transaction fence. It must never await or call
application code while holding these state locks. Real atomic ordering,
durability and crash recovery remain their proper W3--W5/W7 evidence gates.

## 14. Preserved scope, deferrals and review gate

This design preserves CPython >=3.11, supported SQLite >=3.35 with JSON1,
PostgreSQL-primary 15--18 and later stable majors only after real verification,
async-only future public database access, governed writes, one convergent
product, unchanged grammar and standalone `unenforced`.

It does not implement or evidence the W2 planner/bridge/lowering, a production
runtime or worker, PostgreSQL or SQLite adapters, real snapshot provenance,
cross-process coordination, locks, database durability, physical fencing,
credentials, deployment activation, crash recovery, external-write capture,
public names, packaging or deployment. External capture, provider
cryptography, deployment decommissioning and online/mixed-version migration
remain deferred. The accepted W1 terminal wrong-method P3 remains assigned to
W3 with originating closure.

This document does not make the stopped source findings closed, accept itself,
launch implementation or authorize Git/GWZ work. The next gate is manager
pinning followed by fresh peer-blind Consistency and Safety reviews on this
exact document and separate retracing of the originating worker-exit and four
bounded counterexamples. Acceptance requires exact GO/GO and accepts this
replacement design only. A later contract/reference build requires its own
exact execution brief, write boundary and explicit implementation authority.
