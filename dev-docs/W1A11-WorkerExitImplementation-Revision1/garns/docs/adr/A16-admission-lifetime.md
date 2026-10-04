# A16 — Admission and whole-operation lifetime amendment

**Status: PROPOSED FOR INDEPENDENT REVIEW.** This additive internal-contract
decision composes with accepted A2, A3, A6, A8, A11 and A12; it does not edit
or retroactively broaden A1--A15. Names remain provisional until W3 Surface
review. The accepted W2 base plus lifetime overlay controls this decision.

Plans are not executable values. A runtime admits a plan only after binding
validation and deterministic canonical rebuild-and-compare. It issues an
empty, sealed `AdmittedReadHandle`; each finite execution, snapshot,
registration, refresh or iterator handoff separately receives one empty,
sealed `ReadOperationLease`. Issuer-private records alone contain the plan,
provenance, binding, authority, generation, resource ancestry and owner.
Executable backend protocols accept handles/leases, never raw `Plan`. A guarded
consumer is an exact issuer-owned empty identity with fixed behavior and no
caller callback. Only its issuer sees the private plan, atomically commits the
step, then returns a closed step product containing the operation, step, read
identity, digest and lease-pinned detached parameters. Ordinary callables and
cross-issuer or forged consumers refuse before plan access. No external code
runs on a stack retaining the plan or an uncommitted rank.

Static `query` plans admit only finite query/fetch units; bounded `question`
plans admit only registration, refresh and handoff. The closed operation-kind
map derives exact QUERY or LIVE authority. Later caller contexts or parameter
copies cannot replace those pinned at acquisition.

Every operation owns one immutable runtime/pool/connection-or-subscription
ancestry and one shared generation permit from acquisition through lowering,
dispatch, adapter/fetch work, assembly and publication. Owner transfer is
validate-then-commit; a refusal preserves owner, state and charges. Steps move
strictly forward. Child and total fetch commands are sealed finite identities
owned by their parent operation and ordered by parent-local ordinals; they have
no independent acquisition, permit, publication or terminal outcome. One
publication barrier revalidates original authority,
owner, admission/coordinator epochs, binding/generation, permit and local
fences before visibility. Local resources have the
closed states `LOCAL_OPEN`, `LOCAL_DRAINING`, `LOCAL_FENCED` and
`LOCAL_CLOSED`, separately from deployment generation. A local close drains
only its descendants. Cancellation, timeout or `finally` does not establish
quiescence. Resumable work stays `CONTAINED`, charged and visible to close and
migration until authoritative terminal completion. `CloseOutcome` therefore
retains nontransaction `OperationIdentity` values independently from A7
transaction identities and preserves legal `NONQUIESCENT` with no transaction.

Public `TrustedContext` remains empty and task-bound. The lifetime registry is
the sole mutable owner of a finite operation command schedule, its ordered
command ledger, one active command serial, worker authorization, effect
reservation, exit, containment, result acceptance and terminal release.
`WorkerAuthorizationIssuer` is only a stateless façade. Dispatch obtains the
assigned worker and closed effect schedule from fixed trusted setup providers;
ordinary invocation supplies no callback, worker/task identity, stop flag or
containment proof. Each effect ordinal is reserved and removed before the
fixed action begins; nested reservation refuses, and any raised
`BaseException` contains the command and revokes every unused ordinal. Success
remains private until an exact executor-issued stop observation and exact
receiving-task acceptance. Task loss, failure, cancellation and cleanup
failure preserve one primary exit plus bounded diagnostics and retain the
generation charge until authoritative quiescence.

Non-delivery publication atomically records visibility, terminal success and
the one release. Iterator delivery instead uses one specialized success
settlement that atomically records visibility, settles/folds the FIFO head,
terminalizes and releases. Generic completion cannot finish a handoff. Every
precommit non-success retires the registration, invalidates successors, and
retains the active head's charge until exact worker-and-iterator stop and the
specialized second settlement. A commit-first outcome cannot later be
relabeled by close, migration, fence or receiving-task loss.

Deployment participation requires `plan_admission_lifetime_v1`. Activation is
one-time and requires authoritative operator inventory plus a physical legacy
database/file access fence before `ACTIVE_UNUSED(epoch)`; first lifetime open
makes the epoch irreversibly `ACTIVE`. A durable marker or callback is not that
proof. Negative recovery and unused withdrawal require exact binding, epoch,
physical-fence, durable absence/no-ever-open and restored-access proof inputs.
Missing or stale evidence cannot change state, used epochs cannot be reused, and there is
no reset, deactivation or protocol-retirement edge after first open.

Runtime construction is `UNJOINED`: it creates no coordinator participant or
admission authority. An exact lifetime-capable open atomically joins an active
current binding and issues a sealed `ParticipantMembership`. Final local close
requests/finalizes leave only after every retained operation, buffer, worker,
containment and close obligation is gone. A leave requested during migration
remains in that attempt's frozen set, becomes `LEFT` only after attempt close,
and is absent from later attempts.

Migration alone enters deployment-wide `DRAINING_OLD`. One sealed migration
attempt freezes the joined participant set. Every participant installs and
acknowledges its exact pre-zero queue barrier, including an empty queue, before
migration or no-effect reopen. The barrier marks old queues invalidating,
releases each queued buffer permit once, rejects late refresh enqueue and
retains a dequeue winner's active handoff permit. Migration effects wait for
all acknowledgements and the authoritative global count to reach zero; the
requested generation is exactly old generation plus one. Pre-effect refusal
from either `DRAINING_OLD × DRAINING_OLD` or
`MIGRATING × MIGRATING_PRE_EFFECT` may reopen the same binding only with an
exact attempt/phase/serial/request/successor-bound no-effect proof and a new
admission epoch. Request release is observed using the exact current sealed
`MigrationRequestIdentity`; callers supply no evidence digest. The first
migration effect moves the product to `MIGRATING × EFFECT_BEGUN`, permanently
disabling the pre-effect edge. Reopen never resurrects invalid buffers;
unknown post-effect
outcome remains `MIGRATION_INDETERMINATE` until exact proof resolves requested-
next success, full rollback/no-effect under a new admission epoch, or binding
non-reuse. Idle subscriptions hold no execution lease. Registrations and
buffer records privately bind admission, digest, parameters, generation,
queue, separate produced-through/delivered-through FIFO lineage and exact
sealed permit; copied, stale, cross-registration, later-before-head or already-
delivered envelopes cannot change the global count. Initial and refresh
visibility consumes an exact sealed lease-produced candidate containing frozen
rows and watermark/cursor evidence; arbitrary rows or cursors are not a
publication input. Candidate production is explicitly a trusted reference
fixture, not database provenance. Each registration freezes queued capacity
`Q`, changed-lineage capacity `C = Q + 1`, and replay capacity `R = C`.
Changed entries own real permits; coalesced neutral spans own none. A neutral
commit atomically consumes its one current candidate, advances only the legal
frontier, updates the bounded replay ring, terminalizes the refresh and
releases once. Every absent, evicted, cross-registry or counterfeit opaque
handle has the uniform `RefreshRecordUnavailable` result. A known unusable
candidate either returns terminal `RefetchRequired` when quiescent or
`RefreshContainmentPending` until exact worker stop. Overflow, close and
migration discard bounded lineage and retire any active unpublished head.
Local close invalidates selected queued buffers once before reporting `CLOSED`.

## Explicit supersession map

| Existing ADR | Additive A16 refinement |
|---|---|
| A2 backend boundary | Executable plan seams are lease/handle-only; result fields gain exact visible, structural-key and nested-owner roles. |
| A3 async lifecycle | Whole-operation leases, immutable ancestry, contained work and separate retained read identities define close truth. |
| A6 subscription snapshot | Snapshot-registration, refresh and iterator handoff are finite leases; buffer permits participate in generation drain. |
| A8 SQLite async | Worker dispatch uses issuer-private exact-command/effect authorization; public context ownership never transfers. |
| A11 trusted context | Adds only the private worker handshake while preserving the empty task-bound public context and zero-staleness checks. |
| A12 migrations | Requires active lifetime protocol, shared generation permits and the unique pre-zero buffer barrier before effects. |

## Evidence and limits

Candidate deterministic contract evidence is in
`tests/contracts/test_result_roles.py`, `test_admission_contracts.py`,
`test_lifetime_contracts.py`, `test_worker_authority.py` and
`test_generation_contracts.py`, plus the dedicated
`test_worker_exit_contracts.py` and `test_contract_source_rules.py`. It covers
the retained initial/correction causal attacks, exact identity and ordinal
conflicts, worker exit/stop/task-loss ordering, specialized FIFO settlement,
activation-bracketed membership, bounded neutral lineage and the exact
migration phase product. The source checks enforce the raw-`Plan` protocol
boundary and sole mutable owner arrangement.

The historical stopped source and its review rounds remain unchanged evidence.
This implementation is a candidate only: these tests do not close any finding,
and fresh full independent Code/State review plus originating executable
closure on the exact source tuple remain required.

The worker effect counters and reference state models are not actual planners,
lowerers, backends, workers, locks, credentials, processes, threads or
database evidence.
They do not prove canonical production provenance, cross-process generation
coordination, PostgreSQL advisory locks, SQLite file exclusion, crash recovery
or supported-version behavior. Those remain later W2--W5/W7 gates. This ADR
does not self-accept, enable execution or close independent review.
