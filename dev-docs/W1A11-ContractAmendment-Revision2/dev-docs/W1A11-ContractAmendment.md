# W1/A11 admission-lifetime contract amendment

**Status:** remediation 1 builder-complete candidate; fresh independent Code
and State review required; not accepted  
**Date:** 2026-10-04  
**Authority:** `W1A11-ContractAmendment-ExecutionBrief.md`, the manager's
cohesion ownership extension for `generation_reference.py`, and
`W1A11-ContractAmendment-RemPlan.md`

The initial 47-file tuple received independent NO-GO reports (Code: nine P2;
State: eight P2 plus one supplemental bounded P2). That exact history remains
preserved under `W1A11-ContractAmendment-Revision1/`. This document describes
the consolidated correction; it does not claim any finding closed.

## Controlling composition

This amendment implements only internal contract values, protocol signatures
and deterministic reference state/effect tests required by the exact accepted
composition of `W2-QueryPlanningDesign.md` and
`W2-AdmissionLifetimeRedesign.md`. Original A1--A15 and the accepted W2 pair
remain byte-immutable. A16 is additive and supplies this exact supersession:

| Prior decision | Amendment |
|---|---|
| A2 | `ResultFieldRole` is exactly `VISIBLE`, `STRUCTURAL_KEY` or `NESTED_OWNER`; the independent key bit is retained. Executable protocols no longer accept `Plan`. |
| A3 | Each finite unit has an `OperationIdentity`, immutable resource ancestry, one operation lease and explicit owner/state/completion. Close retains operations separately from transactions. |
| A6 | Snapshot registration, refresh and handoff are finite units; immutable buffered envelopes exchange refresh ownership for buffer permits and buffer permits for handoff leases. |
| A8 | Dispatch can issue one private exact-command authorization whose effect ordinals are checked and consumed by the original issuer immediately before effect. |
| A11 | Public contexts remain empty and valid only in their issuing task. Worker authorization references issuer-private state and never transfers public context ownership or claims. |
| A12 | Activation/lifetime capability, deployment generation permits, pre-zero queue invalidation and effect-ordering prerequisites precede migration publication. |

## Required type and method inventory

- Result shape: `ResultFieldRole`, `NESTED_RESULT_TYPE`, amended `ResultField`
  and exact one-to-one `NestedResult` owner validation.
- Admission: `AdmittedReadHandle`, `ReadOperationLease`, `OperationIdentity`,
  `OperationKind`, `AdmissionState`, `LeaseState`, `PlanStep` and
  `PlanAdmissionVerifier.acquire/run_plan_step/transfer_owner/complete`.
- Closed consumers: `ClosedPlanConsumer`, `ClosedStepProduct` and an issuer-
  private registered consumer table; ordinary Plan-taking callbacks are not an
  executable seam.
- Lifetime: `ResourceIdentity`, `ResourceKind`, `LocalResourceState`,
  `DeploymentGenerationState`, sealed `GenerationPermit` and
  `BufferedDeliveryPermit`, `QueueState`,
  `BufferedDelivery`, `ActivationState`, `ActivationEvidence` and
  `SharedGenerationCoordinator`.
- Reference effects: `ReferenceLifetimeRegistry` admission, acquisition,
  guarded steps, ownership, containment, completion, local close, refresh-to-
  buffer, dequeue-to-handoff and queue-barrier transitions; and
  `ReferenceGenerationCoordinator` activation, shared permits, drain,
  no-effect reopen, migration effect, publication and proof-bearing recovery.
- Recovery inputs: `ActivationNoEffectRecoveryProof`,
  `ActivationUnusedWithdrawalProof`, `MigrationRecoveryKind` and
  `MigrationRecoveryProof`.
- Buffer provenance: exact `SubscriptionRegistration` plus issuer-private
  candidate/queued/dequeued/invalid records and cursor lineage.
- Worker seam: `WorkerCommandAuthorization` and issuer-private dispatch,
  exact command-to-worker dequeue, `run_effect` and `revoke`.
- Protocol changes: `AsyncConnection.execute` and `consistent_snapshot` take a
  `ReadOperationLease`; `AsyncBackend.subscribe` takes an admitted handle plus
  initial lease; subscription refresh/handoff require finite leases. There is
  no raw-plan overload, old point-verifier result or `plan_admission_v1`
  fallback.

The cohesion check now separates deployment generation, closed consumers,
buffer provenance, recovery proofs and worker authorization into their own
modules. `lifetime_reference.py` remains 611 lines because its residual
admission, lease, resource, publication and close transitions mutate one
registry-owned state graph; splitting that graph mechanically would obscure
the required validate-then-commit boundaries. Revisit this exception after
independent remediation review or when a real implementation supplies a
transactional state-owner boundary. All modules remain reference evidence.

## Invariants represented

The exact nested marker is
`SemanticType("NestedResult", "structured", list_of=True)`. Reserved `$key.*`
aliases cannot be visible. Structural keys require the role and `key=True`;
every nested owner links exactly once to a child shape. The five accepted W2
vectors are constructed and compared losslessly in `test_result_roles.py`.

Handles are exact-type, sealed, empty, immutable, noncopyable and
nonserializable. Registry records privately retain plan/provenance, binding,
generation, context, resource path and ownership. Production-shaped admission
is explicitly `admit_rebuilt(candidate, rebuilt, binding)`; the separate
`setup_reference_admission` method labels fixture setup and is not claimed as
canonical resolver provenance. Only issuer-owned exact closed consumers are
accepted. Their effects receive `ClosedStepProduct`; ordinary callables,
forged or cross-issuer consumers, properties, wrappers, globals and closures
receive no plan. This is lexical containment, not a return-graph walk.

Acquisition pins detached parameters and the original task-bound context once;
execute/snapshot/subscribe have no second parameter input. Static queries and
bounded live questions have disjoint exact operation-kind grammars. Acquisition
validates admission and coordinator epochs, authority, binding/generation and
all local ancestors before allocating and charging one operation. Every owning
ancestor plus the shared deployment count remains charged until one legal
terminal completion. Identical completion is idempotent; conflicting outcome,
wrong owner/lease or illegal terminal transition refuses without changing
counts. Hard fencing or revocation contains resumable work and suppresses
publication while retaining its permit. Steps are strictly increasing and the
sole publication barrier revalidates authority, owner, admission/registry/
coordinator epochs, binding/generation, exact permit and local fences. A
graceful deployment drain explicitly permits already-pinned old-generation
work. Local close requires an installed drain/fence, invalidates selected
buffers once, never mutates deployment state and leaves peers current.

Worker dispatch derives capability from the closed operation-kind map and
atomically stores authorization with the exact queued command and worker.
Authorization records privately bind the original context record,
runtime, operation, lease, command, worker, binding and finite ordinals. The
issuer uses its own clock/epoch and live operation predicate. Validation and
ordinal consumption precede the supplied effect callback. The callback models
an effect counter only; it is not a worker/thread/adapter implementation.

Activation requires the lifetime capability and complete operator proof-input
shape before a first open changes `ACTIVE_UNUSED` to irreversible `ACTIVE`.
Reference evidence fields do not prove an actual inventory or physical fence.
Missing, stale or mismatched negative evidence cannot resolve indeterminate or
unused activation, and used epochs remain unavailable. The migration queue
barrier discards old buffers once, blocks late enqueue and leaves already-
dequeued delivery work counted. Exact registration/admission/digest/parameters/
generation/queue/cursor provenance is compared at both buffer exchanges. No-
effect reopen increments the admission epoch and invalidates old handles and
leases. Effectful uncertainty has three proof-bearing resolutions: requested-
next success, full rollback/no-effect with a new admission epoch, or binding
non-reuse. Two local registries share one coordinator in schedule tests.

## Test links and evidence classification

| Evidence | What it demonstrates | What it does not demonstrate |
|---|---|---|
| `test_result_roles.py` | exact closed roles, reserved-name abuse, owner/type/cardinality vectors | assembler or SQL behavior |
| `test_admission_contracts.py` | opaque identity/consumer attacks, pinned parameters, disjoint query/live grammar, atomic rejected transfer | production resolver provenance or runtime integration |
| `test_lifetime_contracts.py` | strict steps, unique publication, revoke/fence/drain schedules, exact buffer provenance/counts and local close | actual cancellation, locks, threads, I/O or crash behavior |
| `test_worker_authority.py` | exact queued command/worker/authorization, distinct tasks, original-context expiry, ordinal reuse/revocation | a real worker or cross-process authentication |
| `test_generation_contracts.py` | exact permit ownership, two-participant counts, proof-bearing activation/migration recovery, next-generation isolation | authoritative physical fencing or supported database coordination |
| amended `test_contracts.py` | original attack suite retained under lease-only fake executable seams | public API freeze |

The test suite executes real Python state mutations and callbacks rather than
dispatching on expected answers. It remains pure deterministic reference
evidence. No planner, lowering, backend, async runtime, live engine,
provisioning, migration, credential, activation tool or production coordinator
is implemented or enabled.

## Preserved limits and deferred obligations

- The original accepted W1 Code P3 wrong-method terminal diagnostic remains a
  W3 follow-up and is intentionally unchanged.
- Public names and examples remain provisional for W3 Surface review.
- External-write capture remains deferred.
- No PostgreSQL/SQLite real-server, thread, cross-process, restart, crash or
  physical legacy-fence claim follows from these reference tests.
- `ACTIVE` has no deactivation/reset/protocol-retirement escape; deployment
  decommissioning is out of scope.
- This document does not self-accept, claim Code/State reviewer closure or
  authorize the W2 planner/runtime/backend work.
