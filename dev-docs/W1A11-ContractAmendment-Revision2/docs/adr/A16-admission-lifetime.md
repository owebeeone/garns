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
consumer is an exact issuer-owned empty identity. Only its issuer sees the
private plan, then emits a closed step product containing the operation, step,
read identity, digest and lease-pinned detached parameters. Ordinary callables
and cross-issuer or forged consumers refuse before plan access or effects.

Static `query` plans admit only finite query/fetch units; bounded `question`
plans admit only registration, refresh and handoff. The closed operation-kind
map derives exact QUERY or LIVE authority. Later caller contexts or parameter
copies cannot replace those pinned at acquisition.

Every operation owns one immutable runtime/pool/connection-or-subscription
ancestry and one shared generation permit from acquisition through lowering,
dispatch, adapter/fetch work, assembly and publication. Owner transfer is
validate-then-commit; a refusal preserves owner, state and charges. Steps move
strictly forward, and one publication barrier revalidates original authority,
owner, admission/coordinator epochs, binding/generation, permit and local
fences before visibility. Local resources have the
closed states `LOCAL_OPEN`, `LOCAL_DRAINING`, `LOCAL_FENCED` and
`LOCAL_CLOSED`, separately from deployment generation. A local close drains
only its descendants. Cancellation, timeout or `finally` does not establish
quiescence. Resumable work stays `CONTAINED`, charged and visible to close and
migration until authoritative terminal completion. `CloseOutcome` therefore
retains nontransaction `OperationIdentity` values independently from A7
transaction identities and preserves legal `NONQUIESCENT` with no transaction.

Public `TrustedContext` remains empty and task-bound. Valid task-owned dispatch
atomically records an exact command, worker and private empty
`WorkerCommandAuthorization` for one exact runtime,
lease, operation, command, worker, binding/generation and finite ordinal set.
The issuer checks its original live context record, trusted clock/epoch,
ownership and fences, then atomically consumes one ordinal immediately before
an effect. No task identity or claims move to a worker; wrong, expired,
invalidated, revoked or reused authorization performs no new effect.

Deployment participation requires `plan_admission_lifetime_v1`. Activation is
one-time and requires authoritative operator inventory plus a physical legacy
database/file access fence before `ACTIVE_UNUSED(epoch)`; first lifetime open
makes the epoch irreversibly `ACTIVE`. A durable marker or callback is not that
proof. Negative recovery and unused withdrawal require exact binding/epoch-
bound durable absence/no-ever-open and restored-access proof inputs. Missing or
stale evidence cannot change state, used epochs cannot be reused, and there is
no reset, deactivation or protocol-retirement edge after first open.

Migration alone enters deployment-wide `DRAINING_OLD`. Its unique pre-zero
queue barrier marks old queues invalidating, releases each queued buffer permit
once, rejects late refresh enqueue and retains a dequeue winner's active
handoff permit. Migration effects wait for the authoritative global count to
reach zero. Pre-effect refusal may reopen the same binding only under a new
admission epoch and never resurrects invalid buffers; unknown post-effect
outcome remains `MIGRATION_INDETERMINATE` until exact proof resolves requested-
next success, full rollback/no-effect under a new admission epoch, or binding
non-reuse. Idle subscriptions hold no execution lease. Registrations and
buffer records privately bind admission, digest, parameters, generation,
queue, cursor lineage and exact sealed permit; copied, stale, cross-
registration or already-delivered envelopes cannot change the global count.
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

Pure deterministic contract evidence is in
`tests/contracts/test_result_roles.py`, `test_admission_contracts.py`,
`test_lifetime_contracts.py`, `test_worker_authority.py` and
`test_generation_contracts.py`. It covers exact enum/identity attacks, the five
result vectors, terminal conflicts, local close isolation, authority between
steps, worker revocation/reuse, publication fencing, queue races, migration
timeout ordering and two participants.

The initial independent Code/State review returned NO-GO. Consolidated
remediation 1 corrects its 18 findings across 13 roots; tests do not close
those findings, and fresh independent review remains required.

The reference callbacks and state models are not actual planners, lowerers,
backends, workers, locks, credentials, processes, threads or database evidence.
They do not prove canonical production provenance, cross-process generation
coordination, PostgreSQL advisory locks, SQLite file exclusion, crash recovery
or supported-version behavior. Those remain later W2--W5/W7 gates. This ADR
does not self-accept, enable execution or close independent review.
