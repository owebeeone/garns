# GARNs W1/A11 worker-exit replacement design

**Status:** operator-authorized correction 2/2 design candidate for independent
Consistency/Safety re-verdict; not accepted and not implementation authority  
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
new object was authorized separately by the operator and is now at correction
2 of at most 2 under `W1A11-WorkerExitRedesign-RemPlan-2.md`. There is no
further correction or counter reset authorized by this document.

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
clause, accepted A1--A15 requirement and stopped amendment result-role/
no-raw-Plan claim is retained. Proposed A16 and stopped source remain evidence,
not authority; a later accepted A16 must record this design's exact disposition.

| Controlling clause or candidate claim | Exact additive disposition |
|---|---|
| Accepted overlay §4: “Worker-to-runtime result handoff and worker-to-containment transfer are likewise compare-and-transfer operations naming the expected current owner.” | Completed by §§3--8 below: exact command-exit states, bound receiving runtime task, issuer-owned containment identity, stop observation, replay/conflict rules and publication ordering. For iterator delivery, §8's specialized successful handoff settlement is the only final publication barrier; generic completion cannot terminalize or release that lease. |
| Accepted overlay §4 publication/completion clauses: publication records `PUBLISHING` before visibility, then completion changes it to `SUCCEEDED` and releases. | Refined at the final barrier: `PUBLISHING`/`PUBLICATION_READY` is a nonterminal precommit state, not a separately released outcome. Section 6's generic non-delivery mutation records publication, terminal success and release before exposure. For iterator delivery only, §8's specialized mutation additionally settles the FIFO cursor/head in that same outcome. Neither operation kind has a separately callable releasing completion after publication. |
| Accepted overlay §3.2: task disappearance after dispatch transfers ownership to containment unless authoritative completion exists. | Completed by §§3--7 with an issuer-owned exact receiving-task lifecycle observation. Task done/cancelled explicitly invalidates that operation's original authority and atomically removes queued work or contains every post-dequeue/prepublication state without requiring the vanished task to resume. |
| Accepted overlay §5.1: dispatch binds a command/worker/authorization, later fetch or derived commands receive distinct authority, and each ordinal is consumed immediately before effect. | Strengthened: an operation owns one finite ordered command ledger with at most one active command and retained per-command tombstones; one registry transaction reserves an ordinal and marks an effect in flight before invocation; nested/reentrant reservation refuses; any raised `BaseException` or running cancellation transfers to containment and revokes every unused ordinal before another effect can begin. |
| Accepted overlay §§6--7: hard fencing retains contained work until authoritative quiescence and close distinguishes operations from A7 identities. | Refined with an authoritative executor-issued command-stop observation. A worker return, exception, cancellation, `finally` or cleanup callback is not quiescence. Success is not acceptable or publishable before stop observation. |
| Accepted overlay §8.2: a runtime joins the coordinator at open and a locally closing participant remains registered until retained containment is terminal. | Completed by §9's activation-bracketed sealed membership and exact join/leave grammar. Construction before activation creates no member or admission authority; quiescent final close removes the member from future attempts. |
| Accepted overlay §9 and A6's authored `live bounded N`: only a caller-visible handoff advances delivery; neutral refresh advances internal cursor without a batch; duplicate ranges coalesce within the finite live bound. | Completed by §§8 and 10. The successful handoff settlement atomically publishes, settles FIFO, terminalizes and releases. Registration retirement/refetch follows an unpublished head failure. Changed entries plus coalesced neutral spans, one current candidate per charged refresh operation and bounded replay records have exact bounds, so neutral progress cannot overtake delivery or create an unbounded zero-permit side queue. |
| Accepted overlay §3.1 deployment table/legal-edge paragraph and §8.2 steps 6--8. | Explicitly superseded only for the pre-effect migration edge defined in §11. The exact product state `MIGRATING × MIGRATING_PRE_EFFECT` may return to the same old `CURRENT` once with a current phase/request/successor no-effect proof and new admission epoch. A `DRAINING_OLD` proof is stale there; `MIGRATING × EFFECT_BEGUN` can never use this edge. All post-effect indeterminate rules remain unchanged. |
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
ReceivingTaskLifecycleObservation # issuer-owned exact done/cancel fact
RuntimeContinuationOwner     # issuer-private result receiver identity
WorkerContainmentOwner       # issuer-private failure/cancel owner identity
DeliveryPublicationCandidate # issuer-private nonterminal publication-ready handoff
DeliverySettlementReceipt   # exact committed specialized handoff outcome
DeliveryRetirementReceipt   # exact first-phase failed-head retirement
DeliveryStopObservation     # executor-issued worker+iterator quiescence fact
ParticipantMembership        # coordinator-issued runtime membership
MigrationRequestIdentity     # coordinator-issued phase-specific request
MigrationNoEffectProof       # existing name, strengthened private record
NeutralRefreshReceipt        # exact committed neutral outcome within replay window
```

They are exact-type, identity-compared, immutable, empty, noncopyable and
nonserializable. Their representations expose no runtime, task, context,
claims, plan, lease, command, worker, binding, cursor, result or error. Private
records, not handles, hold those values.

One private lifetime record owns this complete operation tuple:

```text
(runtime identity, operation identity, exact lease, admitted record,
 immutable resource ancestry, generation permit, original context record,
 receiving runtime task and lifecycle serial, RuntimeContinuationOwner,
 finite ClosedOperationCommandSchedule, next command serial,
 ordered command ledger, active command serial or none,
 WorkerContainmentOwner, operation kind, publication/completion record)
```

The closed operation schedule fixes an exact finite positive command sequence
and slot count `M` at acquisition. Every slot is required, issuer-owned and may
describe a primary, later fetch, child, nested or total command derived from
the same parent; no caller may append, skip or replace a slot. The ledger has
at most `M` records, keyed by monotonically
unique operation-local command serial. Each record privately owns its exact
closed command, assigned worker, authorization, immutable effect schedule,
finite trusted cleanup schedule, active reservation, completed/unused ordinals,
exit phase/serial, result or failure, stop bit and terminal tombstone. At most
one record is nonterminal.
Prior records are never overwritten and are retained only until the outer
operation becomes terminal, when the whole bounded ledger is discarded.

The receiving task and assigned worker are captured from trusted injected
providers. They are never method arguments supplied by an ordinary caller.
At dispatch the authority issuer proves that the current task owns the
original context and privately records that task as the sole receiver. At
dequeue, effect reservation and worker exit, the injected current-worker
provider must report the exact assigned worker. At result acceptance, the
injected current-task provider must report the exact recorded receiving task
and A11 validates the original context at zero staleness. Nothing rebinds the
context to the worker.

At dispatch, the trusted task provider also binds a monotonically unique
lifecycle serial. Only that provider may issue a
`ReceivingTaskLifecycleObservation` after the exact task is done or cancelled;
this is a fact read by the registry, not an application callback. In one
lifetime-owner mutation, accepting the exact observation invalidates the exact
original context record in its issuer-owned runtime registry, marks the
operation binding invalid and applies its state-specific removal/containment
transition in §5.2. The context issuer participates in that mutation boundary
but is not a second worker-state owner. No later A11 check can authorize new
work. The observation does not move, disclose or recreate public-context
claims.

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
QUEUE_REMOVED(exit_receipt)
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
QUEUED -> QUEUE_REMOVED                        authoritative queue removal
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

The lease's existing state remains the outer grammar. The first command may
move the outer lease from `ACQUIRED` to `QUEUED`; dequeue moves it to
`RUNNING`. A later command's `QUEUED` is a private ledger state while the same
outer lease remains `RUNNING`; it does not reset the lease or acquire a second
operation/generation permit. Command containment maps the outer lease to
`CONTAINED`. `RESULT_ACCEPTED` is terminal for that command record and returns
ownership to the exact runtime continuation. If its command serial is less
than `M`, the runtime may perform guarded intermediate assembly and atomically
dispatch only the next schedule slot. Public publication is legal only after
serial `M` is `RESULT_ACCEPTED`, no command is active, the exact receiver
remains live and every outer barrier is current. A non-delivery operation then
uses the generic barrier in §6. An iterator-delivery operation instead enters
the nonterminal `PUBLICATION_READY(DeliveryPublicationCandidate)` outer state
and can publish, terminalize and release only through §8's specialized
settlement. Terminal `SUCCEEDED`, `REFUSED` and `CANCELLED_CONFIRMED` remain
outer lease outcomes, not worker-exit states.

`QUEUE_REMOVED` proves only that its exact command did not start. For command
serial 1, with no prior operation work or A7 identity, removal may complete the
outer lease `CANCELLED_CONFIRMED`. Removal of any later serial cannot erase
prior work: it clears the active serial, transfers the already-quiescent outer
lease to the containment owner, and permits only `REFUSED` terminalization
subject to independently retained A7 truth. No later schedule slot dispatches.

### 4.2 Effect reservation and nonreentrancy

Dispatch binds an issuer-owned finite ordered `WorkerEffectSchedule`. Each
ordinal is classified privately as required or optional and names one exact
closed effect command. The runtime, not a caller, constructs that schedule.
Successful command exit requires every required ordinal to have returned; it
atomically revokes any unused optional ordinal.

The worker wrapper's internal operations are conceptually:

```text
dispatch_worker(lease, next_schedule_slot)
  -> WorkerCommandAuthorization
run_effect(authorization, ordinal) -> ClosedWorkerEffectResult
worker_exit_success(authorization, closed_result) -> WorkerExitReceipt
worker_exit_failure(authorization, closed_failure) -> WorkerExitReceipt
request_worker_cancel(lease) -> cancellation disposition
observe_receiving_task_done(lifecycle_observation) -> task-loss disposition
observe_worker_stopped(stop_receipt) -> None
accept_worker_result(exit_receipt) -> ClosedWorkerResult
```

These are issuer-private calls. They take no caller-provided worker identity,
task identity, claims, clock, epoch, binding or containment owner.

`dispatch_worker` validates the exact next unused schedule slot and allocates
the next command serial and record in one mutation. It requires no active
command and either the first-dispatch outer state or the immediately preceding
record at `RESULT_ACCEPTED` under the exact runtime-continuation owner. It then
sets that serial active and queues only its command/authorization. Dispatch out
of order, beyond `M`, before prior acceptance, after receiver loss, or with a
prior command's identity refuses without allocating a record. A contained
command ends the operation schedule; no later slot may dispatch.

`run_effect` first performs one atomic validate-and-reserve mutation under the
lifetime registry owner:

1. require the exact live runtime/operation/lease/active-command-serial/
   command/authorization tuple,
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
atomically marks that record `RESULT_ACCEPTED`, clears its active-command
serial and returns closed result data. Wrong task or wrong tuple refuses mutation-free;
expiry, invalidation or a hard fence closes the result and transfers to
containment because it can never legally publish.

### 5.2 Failure and cancellation

An effect exception is contained by the `run_effect` wrapper before the
exception leaves it and creates the failure exit receipt with
`BEGUN_UNCERTAIN`. The outer wrapper's observation of that same exact receipt
is a replay, not a second exit. A non-effect command-body `BaseException` calls
`worker_exit_failure` and commits its receipt before trusted cleanup begins. It
records `NOT_BEGUN` only if no ordinal was ever reserved and otherwise records
`RETURNED`. Thus the temporally first body/effect/cancel transition owns the
primary receipt and the one containment transfer before cleanup can compete.

Cancellations and invalidations have three trusted sources: a request by the
exact recorded receiving task while its original context is live, an
issuer-internal runtime fence/expiry/close event, or the exact receiving-task
lifecycle observation bound at dispatch. The task and source are obtained from
trusted providers; no caller supplies an owner or claims proof. Queued
cancellation takes the queue lock and either removes the exact command, revokes
its authorization, creates `QUEUE_REMOVED` and applies the serial-sensitive
outer disposition above, or loses to dequeue. After dequeue, cancellation
atomically creates a cancel exit receipt,
records `cancel_requested`, revokes unused ordinals and transfers ownership to
containment. It records `NOT_BEGUN` if no ordinal was reserved, `RETURNED` if
all prior reservations returned, and `BEGUN_UNCERTAIN` if a reservation is
active. This receipt creation applies while the worker still owns
`RUNNING_IDLE` or `EFFECT_IN_FLIGHT`; the post-success case below retains the
already committed success receipt. Cancellation cannot release the permit
until stop observation.

`observe_receiving_task_done` first validates exact issuer, runtime,
operation, context record, receiving task and lifecycle serial without
mutation. Its one accepted commit invalidates the exact original context
record and operation binding, prevents every later schedule dispatch and then
applies exactly one state rule:

- in a queued command, it competes under the same queue lock: removal wins and
  creates `QUEUE_REMOVED`; serial 1 with no earlier work may complete/release
  as `CANCELLED_CONFIRMED`, while a later serial becomes quiescent containment
  and can terminalize only `REFUSED`. Dequeue wins and the running rule below
  owns containment;
- in `RUNNING_IDLE` or `EFFECT_IN_FLIGHT`, it creates the primary task-loss
  cancel exit receipt, revokes unused ordinals, records the correct
  `NOT_BEGUN`, `RETURNED` or `BEGUN_UNCERTAIN` fact and transfers the outer
  lease to containment;
- in `CONTAINED` or `QUIESCENT_CONTAINED`, it preserves the existing primary
  receipt/effect knowledge; task loss occupies only its bounded race-diagnostic
  slot and does not change quiescence;
- in `SUCCESS_PENDING`, it closes the result, retains the success tombstone,
  transfers to containment and waits for exact executor stop;
- in `QUIESCENT_SUCCESS`, it closes the result and moves directly to
  `QUIESCENT_CONTAINED`;
- after `RESULT_ACCEPTED` but before the operation-kind-specific atomic
  publication, including delivery `PUBLICATION_READY`, it closes runtime
  assembly/output and moves the already-quiescent outer lease to containment
  without reopening the command; a delivery lease then uses §8's non-success
  retirement rather than generic completion;
- after terminal publication, it cannot relabel success and is an idempotent
  no-op for that operation.

The containment owner, not the vanished receiver, completes a quiescent
non-delivery operation and releases its one permit; a delivery handoff instead
must pass through both specialized §8 non-success phases and releases only in
their quiescent final settlement. An exact repeated lifecycle observation is
idempotent. A wrong task/context/serial, copy, stale observation from a
prior task reuse, or conflicting lifecycle outcome refuses mutation-free.
Task loss never manufactures A7 abort/commit knowledge.

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
failure cannot reopen the command. A non-delivery lease follows ordinary outer
containment; a delivery lease invokes §8's first retirement phase and retains
its active charge until the specialized quiescent settlement.

### 5.3 Cleanup failure schedule

The required wrapper sequence is:

```text
run command body
  fixed-effect BaseException -> run_effect has committed the primary receipt
  other body BaseException -> commit worker_exit_failure before cleanup
run each finite trusted cleanup step outside the state lock
  if no primary exists, first cleanup BaseException commits the primary receipt
  otherwise cleanup BaseException appends only its step's diagnostic
if body and every cleanup step succeeded -> request success exit
else -> preserve/rethrow the first BaseException and its exact primary receipt
return or rethrow; only after the command frame exits may executor issue stop
```

Success exit is requested only after cleanup returns. Therefore cleanup cannot
fail after a publishable success receipt exists. If cleanup raises after a
result was privately computed and no earlier error exists, that first cleanup
failure is primary, creates the sole exit receipt, closes/discards the result
and transfers to containment. If a body/effect failure or cancellation already
committed, every cleanup failure is secondary. The immutable cleanup schedule
has `K` steps, so a command retains at most one primary plus one diagnostic per
step and one cancellation-race diagnostic; duplicate step/race diagnostics are
idempotent and any different excess record refuses. A cancellation racing
cleanup is first-commit-wins under the registry lock: whichever first creates
the primary receipt keeps it, and the loser can fill only its bounded diagnostic
slot. No diagnostic changes effect knowledge, A7 truth, owner or ordinal sets.

## 6. Idempotency, conflicts and authoritative completion

Every command record has its unique operation-local command serial and one
monotonically unique command-local `exit_serial`. Repeating the same operation
and command serial with the same exact authorization, exit receipt, kind,
closed result/failure digest and exit serial is idempotent against that record's
tombstone. Repeating its stop observation is idempotent. A different command
serial, kind, result, failure, exit serial, lease, authorization, worker,
receiver, runtime, binding or generation is an outcome conflict and changes
nothing.

Closing an authorization retains an immutable private exit tombstone in its
command-ledger record until the operation is terminal. Exact success, failure,
cancel or stop replay for C1 is answered only from C1 even while C2 is queued,
running or accepted. C1's authorization or ordinal can never validate against
C2. A failure/cancel race is therefore first-commit-wins: the loser is only a
bounded diagnostic, cannot replace the receipt or effect knowledge, and cannot
cause a second owner transfer or permit release.

The following never release a generation permit: worker return, success
receipt creation, failure receipt creation, cancellation request, result
acceptance or stop observation by itself. After successful acceptance, the
runtime may continue guarded assembly and reach its operation-kind-specific
publication barrier. For a non-delivery operation, the generic barrier
atomically records publication and terminal `SUCCEEDED`, releases ancestry
charges and the shared permit exactly once, and only then makes the closed
value available to the caller-owned future/channel. For an iterator delivery,
that generic entry is structurally inapplicable: it refuses mutation-free and
cannot set a publication bit, terminalize or release. Section 8's
`settle_delivery_success` is the delivery's sole final publication barrier.
There is no callback between either valid commit and exposure. Exact replay
reads the one committed operation-kind receipt without another exposure,
cursor movement or release; a conflicting completion refuses. A task
cancelled or authoritatively observed done before the applicable commit sees
no publication and follows containment (and, for delivery, §8 retirement)
without the task resuming. A lifecycle observation after the applicable commit
cannot relabel the already published terminal success.

For dequeued contained work, stop observation establishes operation
quiescence, not database outcome. `QUEUE_REMOVED` is independently
authoritative that its exact command never obtained a worker and is therefore
already quiescent; it does not erase earlier operation work. The containment
owner may then complete a non-delivery operation as `REFUSED` or, only for an
authoritatively not-started whole-operation cancellation, as
`CANCELLED_CONFIRMED`, releasing the operation permit once. Generic containment
completion refuses for an active or retiring delivery handoff; only §8's
specialized quiescent non-success settlement can terminalize and release it.
Any A7 transaction identity remains independently retained until its accepted
terminal evidence.
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
observation, result acceptance, publication-ready candidate creation and the
operation-kind-specific final publication. They exercise at least two
sequential commands C1/C2 from one finite operation schedule.

| Trace | Required terminal observation |
|---|---|
| Wrong lease/command/authorization/runtime/generation/current worker at dequeue, effect or exit | refusal before mutation; no effect, ordinal consumption, owner transfer or count change. |
| Effect 1 raises while effect 2 is unused | before the exception escapes, lease is containment-owned, effect 2 is revoked, count remains charged; effect 2 and result exit refuse. |
| Effect attempts nested/reentrant `run_effect` | active reservation makes the nested attempt refuse; outer effect has the sole reservation and the nested attempt consumes nothing. |
| Cancellation loses dequeue race | unused ordinals revoke, running command becomes containment-owned; it stays `NONQUIESCENT` until stop observation. |
| Cancellation between reservation and invocation | reserved effect may begin and is `BEGUN_UNCERTAIN`; no other effect may begin and no result may publish. |
| Local close, context revocation or generation drain races dequeue/reservation/effect/exit | barrier-first refuses before reservation; reservation-first transfers to containment with the charge retained through stop; success-exit-first still cannot cross accept/publication revalidation. Old-generation drain cannot complete from the receipt alone. |
| Body-only; cleanup-only; body+cleanup; effect+cleanup; cancel/cleanup race | a body/effect receipt commits before cleanup; cleanup-only is primary and discards the private result; every later error occupies only its bounded diagnostic slot. All schedules retain one owner/primary receipt and charge through stop. |
| C1 succeeds and C2 is requested under the same operation | C2 refuses before C1 acceptance; after acceptance it gets a new serial/worker/authorization/schedule without another permit. C1 exact exit/stop replay stays idempotent in C1; conflicting C1 failure/cancel and every C1 ordinal/authorization attack refuse without changing C2. Removing queued C2 yields quiescent `REFUSED`, never whole-operation `CANCELLED_CONFIRMED`. One outer terminal release follows the last required slot/publication. |
| Exact receiving task terminates without application cancellation at each pause | its trusted lifecycle observation invalidates the operation context binding; queued work is removed or every later prepublication state is contained, no value publishes, and A7 truth is unchanged. A non-delivery containment owner eventually releases once; a delivery retains its active charge through §8 stop and specialized non-success settlement. Neither requires receiver resumption. Wrong/copy/stale observations refuse; exact replay is idempotent. |
| Worker success while receiving runtime task is wrong/child task | receipt remains private and unaccepted; no claims transfer and no publication. Exact original receiving task may accept only while original context/barriers remain valid. |
| Context expires or runtime hard-fences between success exit and accept | result closes, transition is containment, no publication; stop/quiescence and A7 truth remain independently retained. |
| Success/failure/cancel exit replay | exact replay is idempotent; conflicting replay refuses with one owner, one result and one charge. |
| Late success after failure/cancel containment | closed diagnostic only; no owner, result, terminal state, ordinal or cursor changes. |
| Publication return path raises/cancels before commit | no outward value and no success. After the applicable atomic commit, delivery to the caller-owned future is the publication fact and cannot be relabeled. Iterator delivery proves publication, FIFO settlement, terminal success and the one release share §8's single commit. |
| Last-permit iterator handoff races close/migration/fence/receiver loss immediately before/after final commit | before commit, non-success retirement retains the active charge through exact worker/iterator stop; commit-first atomically publishes, removes/folds the head, terminalizes and releases before exposure. No observation sees count zero with an unsettled head; generic completion refuses; exact settlement replay is read-only. |

## 8. Failed FIFO delivery: registration retirement/refetch

This design selects one fail-closed rule: an exact FIFO head that does not
commit caller-visible publication retires its registration and requires a new
A6 refetch/registration handshake. It is never requeued and successors never
cross it.

A registration has exact states `ACTIVE`, `RETIRING_REFETCH` and `RETIRED`.
An active handoff records one exact FIFO head, handoff lease, iterator
execution identity, bound receiving task/lifecycle serial and outer state:

```text
ACTIVE_HANDOFF
PUBLICATION_READY(DeliveryPublicationCandidate)
RETIRING_HANDOFF(DeliveryRetirementReceipt, cause, stop_pending|quiescent)
COMMITTED_SUCCESS(DeliverySettlementReceipt)
RETIRED_NON_SUCCESS(RefetchRequired)
```

`PUBLICATION_READY` is nonterminal: it has no publication bit and has not
released any ancestry or shared generation charge. Its candidate is created
only after the final required command result is accepted and guarded assembly
is complete. It binds the exact closed value digest, head, lease, registration,
owner, binding/generation and receiving-task lifecycle serial, but exposes no
public-context claims. Candidate creation publishes nothing and releases
nothing. The specialized internal calls are:

```text
settle_delivery_success(handoff_lease, DeliveryPublicationCandidate)
  -> DeliverySettlementReceipt
begin_delivery_non_success(handoff_lease, exact_non_success_cause)
  -> DeliveryRetirementReceipt
observe_delivery_stopped(DeliveryRetirementReceipt,
                         DeliveryStopObservation) -> None
settle_delivery_non_success(handoff_lease, DeliveryRetirementReceipt)
  -> RefetchRequired
```

Every input above is a registry-issued closed record, never a boolean,
caller-selected label, worker/task identity or claims proof. The lifetime
registry remains the sole mutation owner for buffer, handoff, operation and
generation-count facts.

`settle_delivery_success` is the sole final publication barrier for an
iterator handoff. From exact nonterminal `PUBLICATION_READY`, one indivisible
lifetime-owner mutation validates the candidate and handoff lease, exact
runtime-continuation owner, current trusted receiving task and lifecycle
serial, A11 validity of the original context, registration/binding/generation,
local/migration barriers, closed-value digest and current FIFO head. That same
mutation, in this order as one commit:

1. records caller-visible publication and its `DeliverySettlementReceipt`;
2. removes the head, advances `delivered_through` to its `observed_through`
   and folds only its immediately following neutral span under §10;
3. records the outer handoff lease terminal `SUCCEEDED` and removes active
   handoff ownership; and
4. releases its ancestry and one shared generation charge exactly once.

Only after that commit returns may the already closed value be exposed on the
caller-owned future/channel; no callback occurs between commit and exposure.
There is therefore no state with a published value or released last permit and
an unsettled FIFO head. Exact replay reads the one committed settlement
tombstone without another exposure, cursor movement, fold, terminal transition
or release. Different candidate/value/head/lease/owner/task/generation or a
success attempt after retirement is a conflict and changes nothing. The
generic success or containment completion entries in §6 detect the delivery
operation kind and refuse mutation-free, so no earlier terminal outcome,
publication bit or permit release can bypass this transition.

Every legal non-success before that commit uses two phases. First,
`begin_delivery_non_success` validates a registry-owned cause record that has
not terminalized or released the handoff. In one mutation it leaves
`delivered_through` unchanged; marks the head failed and registration
`RETIRING_REFETCH`; invalidates every queued successor and releases each queued
buffer permit exactly once; prevents new refresh, enqueue, dequeue or handoff;
revokes remaining worker/iterator authority; transfers the active handoff to
its preallocated containment owner; and records `RETIRING_HANDOFF`. It does
**not** terminalize or release the active handoff, even when the cause is
cancellation, fence, receiver loss, cleanup failure, close or migration.

Worker-command stop and iterator-frame stop are separate executor facts. Only
the bound executor may issue `DeliveryStopObservation`, and only after both
facts hold. `observe_delivery_stopped` accepts that exact observation only
after the worker command, iterator frame and all finite trusted cleanup cannot
resume. It marks the retained handoff quiescent but neither terminalizes nor
releases it. Cleanup that itself raises is the non-success cause if no earlier
primary exists; otherwise it occupies only its bounded diagnostic slot, and
the charge remains through cleanup and stop. Then, and only then,
`settle_delivery_non_success` atomically records terminal `REFUSED`, removes
the retained active ownership, releases ancestry and the one shared charge,
records `RETIRED` and returns `RefetchRequired`. An active handoff has begun, so
this path can never claim `CANCELLED_CONFIRMED`; only authoritative removal of
a whole operation before any handoff begins may use that outcome under §6.
The settlement never accepts an already-terminal or previously releasing
generic outcome as input.

Exact replay of either phase reads its retained record without another queued
invalidation, stop transition, terminalization or release. A conflicting
success/non-success or cause refuses mutation-free. Produced progress and
diagnostic lineage may be retained, but neither is reported as delivered.
Known later operations on the retired registration return typed
`RefetchRequired`; §10 separately gives an opaque candidate or receipt absent
from all bounded authoritative records the uniform unavailable result, without
pretending to recover its former registration. Close and migration invoke the
same first phase, never double-release queued permits, retain the active charge
while stop is pending, and cannot cross their count/quiescence barrier until
the specialized second phase commits.

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
`ReviewState-2 P2-1` obligations, and for correction-2 `Safety-2 P2-1`. The
mandatory causal regression queues
`(0,1]` and `(1,2]`, fails the first before publication under direct refusal,
authority expiry, local fence, cancellation and cleanup failure, and proves:
delivery stays at 0, the second cannot dequeue, queued permits release once,
the active charge persists through exact worker/iterator stop, repeated
settlement changes nothing, and only a new refetch registration can resume.
The success regression starts with one active head holding the deployment's
last permit, pauses immediately before and after the single success commit,
and races migration, close, fence and receiver loss. It asserts no zero count
with an unsettled head, no exposure before publication/FIFO/terminal/release
all commit, exact replay with no second release, and mutation-free conflict.
Existing two-head successful FIFO and duplicate-success tests remain mandatory.

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

At registration, validate the question's mandatory authored `live bounded N`
against the stricter deployment queued-delivery ceiling and freeze the
resulting positive integer as queued capacity `Q`: `Q = min(N, deployment
ceiling)` when that ceiling is configured, otherwise the default is `Q = N`.
Because there can be at most one active handoff in addition to `Q` queued
changed entries, the exact retained changed-lineage capacity is `C = Q + 1`.
There is no unbounded or omitted-N mode. The neutral replay-window bound `R` is
exactly `C`; this is the internal default and is not caller-configurable. Each
registration owns separate `produced_through` and `delivered_through` cursors,
an ordered lineage and a FIFO replay window of at most `R` exact entries:

```text
CHANGED(previous, observed_through, envelope, QUEUED|ACTIVE|PUBLISHED|FAILED)
NEUTRAL_SPAN(previous, observed_through, PENDING)
NEUTRAL_REPLAY(candidate_identity, receipt_identity, previous, observed_through,
               terminal=SUCCEEDED, release_applied=true)
```

There are at most `C` unabsorbed `CHANGED` entries: at most one active handoff
plus `Q` authored/deployment-bounded queued entries. Consecutive neutral
candidates after the same changed entry coalesce by extending its one
`NEUTRAL_SPAN`; they never append another span in that gap. A neutral candidate
with no earlier unabsorbed changed entry folds immediately and leaves no
lineage record. Thus there are at
most `C` pending neutral spans and at most `2C` retained lineage records. Replay
entries are a separate ring of at most `R == C`; there is no candidate or
receipt side table outside these bounds.

Candidate issuance is separately accounted in the already-existing charged
refresh-operation record. Such a record may hold at most one exact current
issued/unconsumed candidate and its semantic fields. Let `L_refresh` be the
number of currently live charged refresh leases in the existing operation
ledger. The number `A` of current candidate fields obeys the exact invariant
`A <= L_refresh`; it cannot outlive or exist without one of those charged
operations. This is a resource-proportional current-state bound, not a new
caller-configurable history limit. The field is removed on commit, exchange or
terminal containment. Total new neutral-specific retained state is therefore
at most `C` spans, `C` replay entries and `A` current fields in existing
operation records; no evicted candidate or receipt tombstone survives
elsewhere.

A trusted fixed comparator classifies an exact sealed refresh candidate from
its frozen prior/current keyed result. An ordinary caller cannot select the
classification. The sole internal entries are:

```text
commit_refresh(exact_sealed_candidate)
  -> ClosedBatchEnvelope | NeutralRefreshReceipt | RefetchRequired
     | RefreshContainmentPending | RefreshCommitRefused
     | RefreshRecordUnavailable
replay_neutral(NeutralRefreshReceipt)
  -> NeutralRefreshReceipt | RefreshRecordUnavailable
settle_contained_refresh(exact_refresh_lease, exact_worker_stop_receipt)
  -> RefetchRequired
```

Candidate and receipt lookup has one bounded, non-probing grammar. The internal
call receiver fixes the target registry/registration; those values are never
decoded from or supplied alongside the empty handle. For a candidate, the
registry checks only (1) that target's exact current issued/unconsumed candidate
field in a live operation record and (2) that target's `R` replay entries. A
replay hit returns that entry's receipt idempotently without reclassification,
cursor movement, terminalization or release. A current-record hit may proceed
to commit validation below. Any candidate absent from both locations returns
the single typed `RefreshRecordUnavailable`. Receipt lookup checks only the
target's replay ring; absence returns the same `RefreshRecordUnavailable`.
Thus an evicted candidate, evicted receipt, object from another registration or
registry, unknown/counterfeit object and former retired-registration object are
indistinguishable at this interface and all refuse mutation-free. The lookup
does not recover or report a former cursor, classification, registration or
provenance, and cannot select or complete any arbitrary lease.

For a current-record hit, `commit_refresh` revalidates the exact candidate,
lease, operation, registration, admission, parameters, plan digest,
binding/generation, queue, authority, local state, migration marker and exact
`previous == produced_through`, then calculates post-commit lineage/replay
sizes without mutation. A presentation-only mismatch that does not invalidate
the recorded operation returns `RefreshCommitRefused` with candidate, owner,
lease and charge unchanged, so only the original authority can retry. A
current candidate made unusable by cursor divergence, registration retirement,
overflow, close, fence or migration has an explicit operation disposition:

- if its worker is authoritatively quiescent, the same mutation removes the
  candidate from commit eligibility, records terminal `REFUSED`, releases its
  ancestry/generation charge once and returns `RefetchRequired`;
- if its worker may still resume, the mutation removes commit authority,
  transfers the exact refresh lease to containment, retains its charge and
  returns `RefreshContainmentPending`. Only exact worker stop permits
  `settle_contained_refresh` to record terminal `REFUSED`, release once and
  return `RefetchRequired`.

An overflow that would exceed `Q` queued entries, `C` total
active-plus-queued entries, `C` spans or `2C` lineage records also atomically
marks the registration `RETIRING_REFETCH`, invalidates queued successors and
releases their real buffer permits once before applying the known candidate's
quiescent-or-contained disposition above. It does not commit the candidate as
refresh progress or move either cursor. If a handoff head is active, that same
registration transaction also performs §8's first non-success phase: the head
and `delivered_through` remain unsettled, its authority transfers to
containment and its charge remains until exact worker/iterator stop and
specialized final settlement. No `RefetchRequired` is exposed for a known
active refresh candidate until its refresh lease is terminal/released; no
`RefreshContainmentPending` path releases early. Exact lease/stop replay of
`settle_contained_refresh` reads the existing operation tombstone without
another release. Once either terminal route removes the current candidate
field, presenting that opaque candidate is simply absent and returns
`RefreshRecordUnavailable`; it does not receive a history-sensitive result or
release again. No implementation may spill an evicted identity into an
auxiliary table.

A changed commit is one mutation that consumes the current candidate, advances
`produced_through`, appends `CHANGED`, records the refresh operation
`SUCCEEDED_EXCHANGED` and transfers its one ancestry/generation charge to the
new queued buffer permit without a zero-count gap or double charge. A neutral
commit is one different atomic mutation that consumes the candidate, advances
`produced_through`, extends the existing trailing span for that changed-work
gap or creates its sole span, evicts exactly the oldest replay entry if the
ring already holds `R`, appends the new replay record, records the exact
refresh lease terminal `SUCCEEDED`, releases its ancestry/generation charge
once, and returns its `NeutralRefreshReceipt`. It creates no batch, envelope,
buffer permit or delivery publication. Exact candidate or receipt replay while
that entry remains observes the recorded terminal/release facts and performs
no second release. After eviction, both handles receive only
`RefreshRecordUnavailable`; neutral progress cannot make a previous changed
range appear delivered or strand the next changed range.

`delivered_through` advances only by folding a contiguous lineage prefix. A
`CHANGED` record folds only after exact caller-visible publication commit. Its
immediately following coalesced `NEUTRAL_SPAN`, if any, folds in the same
settlement and advances the semantic frontier because caller-visible state did
not change; the span is removed in that mutation and records no delivery or
publication. Folding stops at the next
queued/active/failed changed record. Normal success therefore processes at
most one changed record plus one neutral span; neutral commit evicts at most
one replay entry. Retirement on overflow, failed head, close or migration may
discard at most `2C` lineage records and `C` replay entries, release at most
`C` real delivery permits in its bounded registration mutation, and install
one retirement marker. It does not copy or scan current candidates into a
registration history. Each candidate already named by a charged operation
then observes that marker through the existing per-operation lifecycle and
performs the constant-work quiescent-or-containment rule above. No retirement
waits under the registry lock for a worker stop, and no single neutral-lineage
mutation performs work proportional to lifetime history or to evicted handles.

With zero queued ranges, neutral `(0,1]` advances both cursors immediately
without a delivery. With one or many queued/active changed ranges, neutral
progress advances only `produced_through` and coalesces in the exact preceding
changed-work gap. When that changed record publishes, its one span folds and
the next changed range becomes eligible. Neutral ranges on opposite sides of a
later changed record remain distinct spans and cannot merge across it. If an
earlier changed record fails, registration retirement discards every successor
span/changed record within the stated bound without inventing delivery.

An absent fabricated, copied or cross-registration identity gets only
`RefreshRecordUnavailable`. A known current candidate presented under a wrong
lease/authority refuses with its original owner and charge unchanged; a known
candidate invalidated by generation, fence, migration or trusted
classification failure follows the explicit containment/terminal disposition
above before `RefetchRequired`. Attempting changed publication from a consumed
neutral candidate is a conflict. Close/migration retirement discards
zero-permit spans/replay entries, releases only real queued permits in that
mutation and preserves every nonquiescent refresh charge until exact stop.

This is the prospective design disposition for `ReviewState-3 P2-3`,
correction-1 `Consistency-1 P2-4`/`Safety-1 P2-2`, and correction-2
`Consistency-2 P2-1`/`P2-2`; no source finding is called closed. Mandatory
traces cover zero, one and `Q` queued changed ranges, plus one active head for
the `C == Q + 1` ceiling; one active delayed head followed by substantially
more than `C` neutral refreshes;
multiple changed-work gaps; neutral-neutral-changed and changed-neutral-changed;
replay inside and outside the `R == C` window; earlier head success/failure;
overflow, close and migration; every provenance/barrier attack; and a later
changed range. The neutral-terminal trace starts with one charged refresh and
asserts terminal success, one release, zero buffer permits and zero publication
in the cursor/span/ring commit; it replays and races close/migration on both
sides. The bounded-lookup trace commits far more than `R`, then compares the
oldest evicted candidate/receipt, a live in-window pair, an exact current
issued candidate, a cross-registration pair and counterfeits. It asserts the
uniform absent result, exact live/replay results, no mutation, `A` current
fields only in charged operations, at most `C` replay records and no side
history. Known-candidate overflow/retired/quiescent/nonquiescent cases assert
one explicit terminal or containment owner and one eventual release. Every
trace also asserts the two cursors, coalesced spans, replay-ring size/floor,
queue, active head, permit/publication counts, per-mutation work and refetch
state.

## 11. Phase- and request-exact no-effect proof

A migration attempt privately records:

```text
(attempt identity, phase, phase_serial, old binding, requested binding or none,
 exact phase request identity, protocol/admission epochs,
 frozen participants/acknowledgements, effect_begun, closed)
```

This design explicitly replaces the accepted overlay §3.1 deployment edge set
and §8.2 steps 6--8 only as stated here. Deployment state and active-attempt
phase form one closed product; no other pairing or edge is legal:

```text
CURRENT(old)                x NONE
  -> DRAINING_OLD            x DRAINING_OLD
DRAINING_OLD                x DRAINING_OLD
  -> CURRENT(old,new epoch)  x NONE              exact drain proof
  -> MIGRATING               x MIGRATING_PRE_EFFECT
MIGRATING                   x MIGRATING_PRE_EFFECT
  -> CURRENT(old,new epoch)  x NONE              exact pre-effect proof
  -> MIGRATING               x EFFECT_BEGUN       first migration effect
MIGRATING                   x EFFECT_BEGUN
  -> CURRENT(requested next) x NONE              authoritative success
  -> MIGRATION_INDETERMINATE x EFFECT_BEGUN       any unknown/failure outcome
MIGRATION_INDETERMINATE     x EFFECT_BEGUN
  -> CURRENT(requested next) x NONE              authoritative success recovery
  -> CURRENT(old,new epoch)  x NONE              authoritative full rollback
  -> RETIRED                 x NONE              authoritative non-reuse
CURRENT                     x NONE -> RETIRED x NONE
RETIRED                     x NONE              terminal
```

The one new deployment edge is `MIGRATING × MIGRATING_PRE_EFFECT ->
CURRENT(old,new epoch) × NONE`. It is structurally unavailable after
`EFFECT_BEGUN`; this does not weaken accepted post-effect indeterminacy or allow
ordinary rollback from `MIGRATING`. Entry into `MIGRATING_PRE_EFFECT` is the
accepted step-7 exclusive-permit acquisition and deployment-state change. The
first step-8 effect changes the attempt phase to `EFFECT_BEGUN` before effect
invocation. A no-effect return from either pre-effect phase keeps the same old
binding/generation, publishes a new admission epoch and never resurrects old
buffers. The stopped source and proposed A16 wording are evidence only, not
authority for this supersession.

Every attempt-phase transition increments a monotonically unique attempt-local
`phase_serial`. Entering `DRAINING_OLD` allocates the exact drain request
identity with no requested successor. Entering `MIGRATING_PRE_EFFECT`
increments the serial, allocates a different `MigrationRequestIdentity` and
binds the exact requested successor. Entering `EFFECT_BEGUN` increments the
serial again and permanently disables the pre-effect no-effect edge.

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
change the exact product state to `CURRENT(old,new epoch) × NONE`; only after
that commit may queues reopen under the new epoch. Invalid buffers never
resurrect.

A `DRAINING_OLD` proof is valid only while that exact phase/serial/request is
current. `begin_migration` increments the serial and makes every prior proof
stale. A `MIGRATING_PRE_EFFECT` proof must be issued after that transition and
bind the exact requested successor and exclusive request. Replay, wrong
request, wrong successor, cross-coordinator, cross-attempt and prior-phase
proofs refuse with phase, binding, admission epoch, queue markers, membership,
permit counts and evidence unchanged.

This is the prospective design disposition for the residual
`OriginStateClosure-2 State-Closure-P2-1`, retaining
`OriginStateClosure-1 State-Closure-P2-1`, and correction-1 `Consistency-1
P2-1`. Its mandatory property test enumerates the entire product above and
rejects every other edge/pair. The causal trace issues a DRAINING proof,
completes barriers, enters `MIGRATING × MIGRATING_PRE_EFFECT` on the same
attempt and proves the old proof refuses mutation-free; a newly issued exact
pre-effect proof reopens once. That proof after `EFFECT_BEGUN`, plus replay,
wrong request/successor, cross-attempt and cross-coordinator variants, refuses
with binding, epochs, phase serial, request, queue markers, membership and
permit counts unchanged.

## 12. Complete finding and regression disposition

The five stopped roots receive these exact design dispositions; none is called
closed on source because this is design only.

| Root and all stopped IDs | Design disposition | Mandatory later evidence |
|---|---|---|
| Worker exit — `ReviewState-3 P2-1` | §§3--7 define the finite multi-command ledger; exact success, failure, cancellation and receiver-loss transfers; result receipt; stop observation; receiver trust; containment and terminal release. | Deterministic causal traces in §7, syntax-aware transition/owner/ordinal checks, then real async/thread executor tests at W3. |
| Failed FIFO — `ReviewCode-3 P2-1`; `ReviewState-3 P2-2`; `FreshCodeClosure-2 P2-1`, retaining `ReviewCode-2 P2-2`/`ReviewState-2 P2-1` | §8 selects registration retirement/refetch; its specialized success commit is the only handoff publication/terminal/release barrier, and its two-phase non-success retains the active charge through quiescence. | Last-permit and two-range failure/success, every non-success, replay, receiver loss, close and migration traces with exact cursors/counts. |
| Participant lifecycle — `ReviewCode-3 P2-2` | §9 makes membership activation-bracketed and leave quiescence-bound without mutating frozen attempts. | Pre/post activation, drain, migration and local-close topology traces. |
| Neutral refresh — `ReviewState-3 P2-3` | §10 adds sealed neutral consumption, atomic refresh terminal/release and capacity-bounded, coalesced zero-permit lineage/replay across queued/active ranges. | Zero/one/multiple range, capacity, provenance, barrier, failure, uniform unavailable replay and retirement traces. |
| Phase proof — `OriginStateClosure-2 State-Closure-P2-1`, retaining `OriginStateClosure-1 State-Closure-P2-1` | §11 explicitly supersedes the accepted migration edge and binds proof to exact product phase/serial/request/successor. | Full product enumeration, same-attempt cross-phase trace, exact current pre-effect success and every post-effect/replay/cross/wrong variant. |

Correction 1 has five roots across six filed IDs. These are prospective design
dispositions only and require reviewer retracing:

| Correction-1 ID(s) | Integrated disposition | Mandatory later evidence |
|---|---|---|
| `Consistency-1 P2-1` | §2 names and §11 exactly replaces the accepted deployment-edge/step-7 conflict with one proof-gated pre-effect product edge. | Enumerate every product edge; stale DRAINING, exact pre-effect once, post-effect, wrong/replay/cross variants with full unchanged-state assertions. |
| `Consistency-1 P2-2` | §§3--6 replace singular command fields with an operation-owned schedule of at most `M` records, one active serial and retained per-command tombstones under one permit. | C1 then C2; premature C2; every C1 receipt/auth/ordinal against every C2 state; one outer release. |
| `Consistency-1 P2-3` | §5 commits non-effect body failure before cleanup; cleanup-only failure is primary; effect/body/cancel winners retain primary ordering and bounded diagnostics. | Body-only, cleanup-only, body+cleanup, effect+cleanup and cancel/cleanup first-commit schedules. |
| `Safety-1 P2-1` | §§3--8 add exact provider-issued receiving-task lifecycle observation, explicit context-binding invalidation and fail-closed transitions from queue through accepted-before-publication. | Terminate the receiver at every pause without application cancellation; wrong/stale/copy/replay observation attacks; operation-kind-specific eventual release without task resumption. |
| `Consistency-1 P2-4`; `Safety-1 P2-2` | §10 sets queued `Q` from validated authored/deployment capacity, total `C == Q + 1`, `R == C`, coalesced spans, `2C`/`C` storage ceilings, deterministic bounded eviction/unavailability and bounded settlement/retirement work. | Exceed `C` neutral refreshes behind delayed work, multiple gaps, inside/outside-window replay, next changed range, success/failure/overflow/close/migration. |

Correction 2 has three bounded findings and makes these additive prospective
dispositions. The full-review NO-GOs override the narrower correction-1 GOs;
none of these IDs is called closed by this document:

| Correction-2 ID | Integrated disposition | Mandatory later evidence |
|---|---|---|
| `Consistency-2 P2-1` | §10 makes candidate consumption, neutral cursor/span/ring commit, refresh terminal `SUCCEEDED` and its one release atomic. Every known current-candidate refusal/refetch route either retains the unchanged live owner, terminalizes/releases when quiescent, or contains until exact stop; replay never releases. | Charged neutral success to count zero/buffer zero/publication zero; exact candidate/receipt replay; close/migration before/after; overflow and retired known candidates in quiescent/nonquiescent states. |
| `Consistency-2 P2-2` | §10 recognizes only the finite current candidate field in each charged operation and the `R == C` replay ring. Every opaque candidate/receipt absent there returns uniform `RefreshRecordUnavailable`; no post-eviction cursor/provenance recovery, semantic handle fields or side history exists. | Far more than `R` commits; evicted and in-window pairs; current issued candidate; cross-registration and counterfeit identities; exact `A`/`C` storage and unchanged-state assertions. |
| `Safety-2 P2-1` | §§4--8 make specialized `settle_delivery_success` the sole handoff final barrier and one atomic publication/FIFO/terminal/release outcome. Generic completion cannot bypass it. Specialized two-phase non-success invalidates successors but retains the active charge until exact worker/iterator stop, then alone terminalizes/releases. | Last-permit pauses around the single commit raced with migration/close/fence/task loss; no exposure or false zero count; replay/conflict; all non-success causes with one queued invalidation and one quiescent release. |

All earlier successful attacks remain mandatory regressions. The initial 18
IDs are `ReviewCode P2-1` through `P2-9`, `ReviewState P2-1` through `P2-8`,
and `ReviewState-Supplement P2-1`; expanded revocation under State P2-4 remains
explicit. The stopped amendment correction-1 13 IDs are `ReviewCode-2 P2-1`
through `P2-3`,
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
| `src/garns/backends/contracts/lifetime_reference.py` | Sole deterministic mutation owner for lease, finite command ledger, current refresh-candidate field, authorization, reservation, worker exit, receiving-task loss, delivery publication/settlement, containment, result acceptance, terminal release and cross-ledger atomic ordering. Generic completion rejects handoff operations. |
| `src/garns/backends/contracts/buffer_reference.py` | Capacity-bounded registration lineage/replay and two-phase retirement subledger, including FIFO settlement inputs, mutated only inside a lifetime-registry transaction. It owns no independent terminalizer or permit release. |
| `src/garns/backends/contracts/snapshot_reference.py` | Empty sealed changed/neutral candidate identities and fixed trusted classification; semantic fields live only in current operation/replay records, with no database provenance claim or evicted-identity history. |
| `src/garns/backends/contracts/generation_reference.py` | Sole membership, generation count, attempt phase/request and proof-consumption owner. |
| `src/garns/backends/contracts/migration_reference.py` | Empty migration/membership/request/proof types and private record shapes, not an independent coordinator. |
| `src/garns/backends/contracts/lifetime.py`, `protocols.py`, `values.py` | Shared closed values/refusals and provisional internal seams; no public freeze. |
| `tests/contracts/test_worker_authority.py`, `test_admission_contracts.py`, `test_lifetime_contracts.py`, `test_generation_contracts.py` | All mapped deterministic transitions, including two-command isolation, receiver loss, primary-exit ordering, specialized handoff publication/retirement, neutral terminal/release and bounded unavailable lookup, and the migration product; a separate `test_worker_exit_contracts.py` is justified only if the later brief assigns it as the focused causal schedule, not to split assertions by line count. |
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

This document does not make the stopped source findings, correction-1 review
findings or correction-2 review findings closed, accept itself, launch
implementation or authorize Git/GWZ work. This edit consumes correction 2/2;
there is no hidden third correction. The next gate is manager pinning followed
by focused re-verdicts from the same peer-blind Consistency-2 and Safety-2
reviewers on their exact three IDs plus changed-range attacks, and retracing of
the relevant originating worker-exit and four bounded counterexamples on the
same tuple. Acceptance requires the exact required GO/GO and originating
closure, and accepts this replacement design only. Any new architectural root
after this correction requires STOP and operator direction. A later
contract/reference build requires its own exact execution brief, write
boundary and explicit implementation authority.
