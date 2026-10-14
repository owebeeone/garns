# W1/A11 worker-exit contract/reference implementation

**Date:** 2026-10-05 (corrections 1 and 2 of 2 applied; initial object
2026-10-04)  
**Status:** candidate implementation after the last allowed consolidated source
correction; round-3 Code/State review and the re-verdicts of every round-2
reviewer who raised an open finding are pending  
**Authority:** `W1A11-WorkerExitImplementation-ExecutionBrief.md`, the accepted
worker-exit design/acceptance tuple named there, and the controlling
remediation dispositions `W1A11-WorkerExitImplementation-RemPlan.md` and
`W1A11-WorkerExitImplementation-RemPlan-2.md`

This document records the enacted deterministic contract/reference object as
corrected. It does not accept A16, close a finding, authorize a production
runtime, or alter the stopped source/design histories. Correction 1 resolved
the thirteen blocking roots IR1–IR13 and the non-blocking roots IR14–IR19 of
the RemPlan; every round-1 finding was then closed by its raiser on
MANIFEST-2. Correction 2 resolves the round-2 roots IR21–IR26, IR29 and IR30 of
RemPlan-2. IR27 and IR28 are deferred to W3 by operator decision; IR20 stays
outside the write boundary.

## Enacted ownership and type inventory

`ReferenceLifetimeRegistry` is the sole mutable owner of operation leases,
finite command schedules, ordered command ledgers/tombstones, the active command
serial, worker authorization, effect reservation, primary exit and cleanup
diagnostics, receiving-task lifecycle, result escrow/acceptance, containment,
delivery publication/retirement, current refresh candidates and terminal
release. `ReferenceBufferRegistry` is its transactional FIFO/lineage subledger;
it never releases a generation permit. `ReferenceGenerationCoordinator`
continues to own deployment permits, activation-bracketed membership, the
registry-witnessed leave and the migration attempt phase/request product.
`WorkerAuthorizationIssuer` contains only two delegation callables, `run_effect`
and `context_owner`, and owns no record table; it offers no cancellation
route, so the design's three trusted cancellation sources (live receiver,
issuer-internal fence/expiry/close event, exact receiving-task lifecycle
observation) are the only ways into containment. The registry is typed
against, and checks conformance with, the formal `SharedGenerationCoordinator`
seam in `lifetime.py`, which now also declares `recover_migration`, the exit of
`MIGRATION_INDETERMINATE`.

The enacted sealed empty identities are unchanged by the correction:

- worker: `WorkerCommandAuthorization`, `WorkerEffectReservation`,
  `WorkerExitReceipt`, `WorkerStopReceipt`,
  `ReceivingTaskLifecycleObservation`, `RuntimeContinuationOwner`,
  `WorkerContainmentOwner`, `ClosedWorkerCommand`, `ClosedWorkerResult`, and
  `ClosedWorkerFailure`;
- delivery: `DeliveryPublicationCandidate`, `DeliverySettlementReceipt`,
  `DeliveryRetirementReceipt`, and `DeliveryStopObservation`;
- membership/migration: `LifetimeOpenRecord`, `ParticipantMembership`,
  `MigrationAttempt`, `MigrationBarrierAcknowledgement`,
  `MigrationRequestIdentity`, and `MigrationNoEffectProof`;
- neutral refresh: `RefreshSnapshotCandidate` and `NeutralRefreshReceipt`.

They are exact-type/identity compared, empty, immutable, noncopyable and
nonserializable. Semantic values remain only in issuer-private records.
`MigrationParticipant` is a compatibility alias of `ParticipantMembership`.

The principal enacted transitions are `open_lifetime`, `dispatch_worker`,
`dequeue_worker`, `run_worker_effect`, `worker_exit_success`,
`worker_exit_failure`, `run_worker_cleanup`, `request_worker_cancel`,
`observe_worker_stopped`, `observe_receiving_task_done`,
`accept_worker_result`, `run_plan_step`, `register_subscription`,
`commit_refresh`, `publish_refresh_buffer`, `replay_neutral`,
`settle_contained_refresh`, `dequeue_buffer`, `prepare_delivery_publication`,
`settle_delivery_success`, `begin_delivery_non_success`,
`observe_delivery_stopped`, `settle_delivery_non_success`, `start_close`,
`close_outcome`, `migration_queue_barrier`, `revoke_generation`; and on the
coordinator `join_runtime`, `close_unjoined`, `witness_local_drain`,
`witness_local_close`, `request_leave`, `finalize_leave`,
`observe_request_released`, `reopen_no_effect`, `begin_migration` (now
returning the phase `MigrationRequestIdentity`), `begin_migration_effect` and
the explicit refusal `retire_binding`.

Closed observers added for refusal testimony: `lease_facts(lease)` reports
(state, completion, owner label, active serial, ledger length) with the owner
as a label and never an identity; `worker_cleanup_step(authorization)` reports
the next cleanup step; `admission_state(handle)` reports an admission record's
state label. `worker_exit_facts` counts a late-return diagnostic in its
diagnostic count.

Fixed `command_schedule_provider`, `assigned_worker_provider`,
`effect_provider`, and `cleanup_provider` values are installed only at trusted
reference setup. Per-invocation worker entries accept no effect callback,
worker/task identity, stop boolean, containment owner or caller-composed proof.

## The seven shared mechanisms of correction 1

| Mechanism | Where it lives | Roots |
|---|---|---|
| One publication precondition: ledger length equals `M`, last record `RESULT_ACCEPTED`, no active command, exact continuation owner, live and current receiver | `_publication_ready` / `_require_publication_ready`, required by `run_plan_step` (PUBLICATION), `register_subscription`, `_commit_refresh_record`, `prepare_delivery_publication`; `complete(SUCCEEDED)` is only an exact replay after publication | IR1, IR2 |
| One containment routine that leaves terminal and retiring leases alone, moves lease, command and result together, routes deliveries into §8 phase one with a registry-owned cause and transfers to the containment owner | `_contain_lease` (with `_contain_command` for the command record and `_begin_retirement` for phase one); every writer of `CONTAINED`, `RETIRING_HANDOFF` or the containment owner is one of these, enforced by a source rule | IR3–IR6, IR12 |
| Presentation refusals never contain | `_presentation_current` checked before barrier validation in `_validate_barriers` and `_commit_refresh_record`; `CONTEXT_OWNER_MISMATCH` never reaches containment | IR3 |
| Validate-before-mutate worker entries | `run_worker_cleanup` validates active serial, current worker, step and legal state before its containment scope, refuses while its own cleanup action is on the stack, and claims the step atomically with that validation before the action runs (a claimed step is consumed whether the action returns or raises); `run_worker_effect` refuses once cleanup has begun; `dispatch_worker` validates every serial's outer lease and keeps later slots' outer state `RUNNING`; `accept_worker_result` requires the exact escrow-owned outer state; a non-worker late success refuses before any diagnostic is recorded | IR7, IR8, IR23, IR25 |
| Refresh disposition routing | `_commit_refresh_record` checks lineage, registration state and coordinator `CURRENT` inside the guarded validation and routes every unusable outcome through `_dispose_refresh`, discarding a failed `CANDIDATE` record in the same mutation | IR11 |
| Registry-witnessed leave and membership binding | `witness_local_drain`/`request_leave` behind `start_close(runtime)`; `witness_local_close` on a CLOSED outcome finishes the leave now or at attempt close; admissions, leases, buffer permits and exchanges bind the exact JOINED membership and refuse after `LEFT`; `open_lifetime` and `_admit` refuse once the runtime resource has left `LOCAL_OPEN` or a runtime close has begun, so a never-joined closing registry proceeds only `UNJOINED -> LEFT` through `close_unjoined`; `close_outcome` performs the coordinator witness before its first local mutation, and a repeated `start_close` never relabels RETIRED or REVOKED admissions | IR9, IR14, IR21 |
| Complete coordinator protocol | `SharedGenerationCoordinator` declares every member the registry calls with exact identity types, plus `recover_migration`; the registry is typed against it and checks `isinstance` at construction; a source rule enumerates every public registry entry that can reach the containment routine and requires each to validate a receiver, an assigned worker, or a trusted observation or barrier first | IR10, IR22, IR29 |
| Bounded retention with indexed lookups | `_terminalize` → `_discard_operation_history` discards the ledger and per-command maps, clears the active command serial and discards an unconsumed initial-snapshot candidate; indexes `_authorizations`, `_exit_receipts`, `_refresh_candidates`, `_retirements`, `_handoff_leases` and the buffer registry's replay index give constant-work lookups; completed, invalid and failed-candidate buffer records are pruned; a late delivery-stop setup on a settled retirement replays or refuses | IR13, IR24, IR26 |

## Exact accepted supersession map

| Accepted or historical clause | Enacted additive disposition |
|---|---|
| Overlay §4 worker-to-runtime/containment compare-and-transfer | Exact command exit, receiving task, containment owner, stop observation, receiver acceptance and operation-specific publication form the transfer; every containment goes through one ledger-aware routine. |
| Overlay §4 `PUBLISHING` then separately releasing completion | Non-delivery publication (EXECUTE/CONSISTENT_SNAPSHOT publication, snapshot registration, neutral and changed refresh commit) atomically publishes, terminalizes and releases behind the one publication precondition; iterator handoff uses only its specialized atomic success settlement. Generic `complete(SUCCEEDED)` is an exact replay only. |
| Overlay §3.2 task disappearance and terminal absorption | Exact lifecycle observation invalidates the original context, removes queued work with a CANCEL receipt or contains every later prepublication state without receiver resumption; terminal leases absorb every later entry. |
| Overlay §5.1 one dispatch/effect ordinal | One finite operation schedule owns distinct command records/tombstones, one active serial and reserve-before-invoke nonreentrant effects; every slot is required and every serial validates the outer lease before dispatch. |
| Overlay §§6--7 quiescence and hard fence | Exact executor-issued stop is required; return, exception, cancellation, cleanup/finally and known result do not establish stop. A hard fence moves every remaining selected lease, including a continuation-owned accepted one, to containment. |
| Overlay §8.2 participant lifetime | Construction is `UNJOINED`; the first join performs `ACTIVE_UNUSED -> ACTIVE`; leave is registry-witnessed, obligation-bound (generation and buffer permits) and frozen-attempt-bound; a `LEFT` member admits, acquires, enqueues and exchanges nothing. |
| Overlay §9 / A6 neutral progress | `Q`, `C=Q+1`, `R=C`, coalesced neutral spans, current charged candidates and the bounded replay ring make neutral commit terminal and bounded; cursor divergence, retirement and migration give the explicit §10 disposition. |
| Overlay §3.1 / §8.2 migration edge | Only the exact current `MIGRATING × MIGRATING_PRE_EFFECT` phase/request/successor proof may reopen old/current; `EFFECT_BEGUN` disables it and a second effect refuses; `CURRENT -> RETIRED` is an explicit refusal pending separate decommissioning authority. |
| Stopped per-call effect callback seam | Replaced by issuer-owned closed commands and fixed setup actions; ordinary effect invocation is `(authorization, ordinal)`. |
| Stopped frontier plus active-head buffering | Replaced by outcome-sensitive FIFO success settlement and two-phase registration retirement/refetch with bounded neutral lineage; queue removal, barrier failure, fence, revocation and receiver loss all enter phase one with a registry-owned cause. |

All other accepted W1/W2 truths remain unchanged: raw `Plan` is absent from
execution protocols; result roles and five result vectors remain intact;
parameters/binding/generation/ancestry/kind remain pinned; derived commands have
no independent permit; public context remains empty and task-bound; A7 outcome
knowledge remains independent; local close remains distinct from migration.

## Executable regression disposition

The existing suites retain the original admission, result-role, lifetime,
generation and product attacks; every fixture that published without a command
now drives the default slot (`run_command`). Retained attacks were adapted,
never deleted; the adaptations are listed in the correction-1 testimony.

| Root | Closure tests (`tests/contracts/test_worker_exit_contracts.py` unless noted) |
|---|---|
| IR1 publication precondition | `PublicationPreconditionTests`: every kind × default/distinct worker × zero/queued/running/success-pending/quiescent stage refuses unchanged; two-slot schedule refuses after C1 and from inside the effect, then succeeds exactly once; migration refuses while a command can run; source rule `test_terminalizers_are_exactly_enumerated_and_gated` |
| IR2 atomic registration | `test_registration_is_one_atomic_publication_terminal_release`, `test_registration_failure_before_commit_leaves_no_registration` |
| IR3 presentation refusals | `ContainmentRoutineTests.test_wrong_task_refresh_commit_is_presentation_only`, `test_worker_presenting_the_current_owner_on_a_plan_step_is_refused_without_mutation` |
| IR4 containment routine | `test_barrier_failures_move_lease_and_command_together`, `test_barrier_inside_the_effect_contains_with_exact_knowledge`, `test_expiry_at_dequeue_has_serial_sensitive_terminal_outcomes`; source rule `test_containment_writes_live_in_one_routine` |
| IR5 queue removal and registry-detected non-success | `test_queue_removal_returns_a_cancel_receipt_for_every_kind`, `test_registry_detected_delivery_non_success_enters_phase_one` |
| IR6 terminal absorbing / retiring survives | `TerminalAbsorptionTests` |
| IR7 cleanup validation | `WorkerEntryValidationTests` cleanup tests |
| IR8 later-slot dispatch | `test_later_slot_dispatch_validates_the_outer_lease`, `test_retired_delivery_never_dispatches_a_later_slot` |
| IR9 registry-witnessed leave | `MembershipLeaveTests` (first three tests); retained `MembershipAndPhaseCausalTests` adapted |
| IR10 coordinator seam | `CoordinatorProtocolTests`; source rule `test_coordinator_protocol_members_equal_accepted_call_shapes` |
| IR11 refresh disposition | `RefreshDispositionTests` |
| IR12 hard fence | `test_hard_fence_contains_accepted_unpublished_leases` |
| IR13 bounded retention | `RetentionBoundTests` (weak-reference liveness and a deterministic call-event counter) |
| IR14 first-open join | `test_first_join_activates_and_withdrawal_stays_available_until_then` |
| IR15 replay exactness | `ReplayExactnessTests` |
| IR16 enumeration and source rules | `CommandGrammarEnumerationTests`, `MigrationProductTests`, and the four new/extended rules in `test_contract_source_rules.py` |
| IR17 phase guard | `MigrationProductTests.test_second_migration_effect_and_current_retirement_refuse_without_change` |
| IR18 dequeue validation | `DequeueAndRemovalLabelTests.test_invalid_handoff_schedule_leaves_count_permits_head_and_registration_unchanged` |
| IR19 serial-1 label | `DequeueAndRemovalLabelTests.test_serial_one_removal_label_depends_on_prior_plan_work` |
| IR21 join after close begun (round 2: ReviewCode-2 P2-1, ReviewState-2 P2-1, OriginCodeClosure-1-Reverdict P2-8, OriginStateClosure-1-Reverdict P2-8, ReviewCode-1-Reverdict P3-8) | `JoinAfterCloseTests`: join refuses after graceful and hard close on an unjoined registry, close proceeds `UNJOINED -> LEFT`, later attempts require only live members and migrate/reopen; close refusals (barrier missing, injected coordinator-witness refusal) leave resources, admissions and membership unchanged; repeated close never relabels RETIRED/REVOKED admissions |
| IR22 façade route (ReviewCode-2 P2-2) | `FacadeRouteTests`: third-task interlude at QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT, SUCCESS_PENDING and QUIESCENT_SUCCESS on EXECUTE and a two-range delivery leaves the vector unchanged; the façade exposes only `run_effect` and `context_owner`; source rule `test_public_containment_entries_validate_authority_first` |
| IR23 cleanup claim (ReviewState-2 P2-2) | `CleanupClaimTests`: same-step and next-step re-entry refuse unchanged, actions run exactly `[1, 2]`, success exit and publication wait for both steps, a raising action still consumes its claimed step, effect reservation refuses during and after cleanup |
| IR24 active serial (ReviewCode-2 P3-2, ReviewState-2 P3-1, OriginStateClosure-1-Reverdict P3-4) | `TerminalTombstoneTests.test_every_terminal_route_clears_the_active_serial`, `test_late_delivery_stop_setup_after_settlement_replays_without_indexerror` |
| IR25 late-return authority (ReviewCode-2 P3-1, ReviewState-2 P3-2) | `LateReturnAuthorityTests` |
| IR26 initial candidates (ReviewCode-2 P3-3, OriginStateClosure-1-Reverdict P3-6) | `TerminalTombstoneTests.test_unconsumed_initial_candidates_die_with_their_operation` |
| IR29 seam exit (ReviewCode-2 P3-4) | `CoordinatorProtocolTests` (a stub lacking `recover_migration` does not conform); source rule member set |
| IR30 issuing-task effect (ReviewCode-1-Reverdict P3-7 residual) | `WorkerEntryValidationTests.test_issuing_task_cannot_run_an_effect_after_a_distinct_worker_dequeued` |
| IR31 in-frame success exit (correction 3, RemPlan-3: ReviewCode-3 P2-1, ReviewState-3 P2-1, ReviewCode-2-Reverdict P2-3, ReviewState-2-Reverdict P2-3, OriginCodeClosure-1-Reverdict-2 P2-9, OriginStateClosure-1-Reverdict-2 P2-9) | `CleanupInFlightSuccessExitTests`: `worker_exit_success` also refuses while `cleanup_in_progress` (the one changed source line, `lifetime_reference.py` line 664), so a success request made from inside the final cleanup action refuses with the full vector unchanged. EXECUTE, raising final action, K = 1 and 2: the cleanup failure is the primary FAILURE, the command is CONTAINED under the containment owner, publications stay 0 and `complete_contained` gives REFUSED with count 0. EXECUTE, returning final action, K = 1 and 2: success exit is accepted once after the action returns and publishes once. Two-range `ITERATOR_HANDOFF`, K = 1, raising final action: `RETIRING_HANDOFF`, successor released once, cursors stay (2, 0), successor dequeue refuses, and settlement returns `RefetchRequired` with count 0. `CleanupClaimTests` (IR23) checks success exit only between steps, so this class supplies the in-frame interleaving it did not exercise |

The five stopped roots and later residuals keep their mapping:

| Root / retained IDs | Stateful regression locations |
|---|---|
| Worker exit (`ReviewState-3 P2-1`, `Consistency-1 P2-2/P2-3`, `Safety-1 P2-1`) | `test_worker_authority.py`; `WorkerExitCausalTests`; `PublicationPreconditionTests`; `ContainmentRoutineTests`; `WorkerEntryValidationTests`; `CommandGrammarEnumerationTests`. |
| Failed FIFO (`ReviewCode-3 P2-1`, `ReviewState-3 P2-2`, `FreshCodeClosure-2 P2-1`, `Safety-2 P2-1`) | delivery success, first-head failure with successor invalidation, receiver loss, precommit expiry/fence/migration, commit-first late barriers, queue-removal and registry-detected retirement, retiring survival, later-slot refusal, plus retained two-head success/invalidation/close tests. |
| Participant lifecycle (`ReviewCode-3 P2-2`) | unjoined admission/close, pending leave in frozen attempt, later-attempt absence, copy/cross/stale membership, join-during-drain refusal, `MembershipLeaveTests`, `CoordinatorProtocolTests`. |
| Neutral refresh (`ReviewState-3 P2-3`, `Consistency-1 P2-4`, `Safety-1 P2-2`, `Consistency-2 P2-1/P2-2`) | zero-queue atomic neutral, delayed changed head/span fold, more-than-`R` replay eviction, active+`Q` overflow, changed-neutral-changed gaps, nonquiescent known-candidate stop settlement, `RefreshDispositionTests`, `RetentionBoundTests`. |
| Phase proof (`OriginStateClosure-1/2 State-Closure-P2-1`, `Consistency-1 P2-1`) | stale same-attempt drain proof, exact current pre-effect proof, effect-begun refusal, exact serial/request transitions, wrong request and replay/cross proof tests, `MigrationProductTests`. |

Initial-18 and correction-1 13/F1--F10 coverage remains distributed through
`test_result_roles.py`, `test_admission_contracts.py`,
`test_lifetime_contracts.py`, `test_worker_authority.py`,
`test_generation_contracts.py`, and `test_contracts.py` as before.

`test_contract_source_rules.py` parses every owned Python contract source and
checks the no-raw-`Plan` protocol boundary, the exact worker-entry signature
set (now including `run_worker_cleanup` and `observe_receiving_task_done`),
the stateless worker façade with no cancellation route, the single
shared-permit release site (`_terminalize` only), single
cursor/membership/proof-construction owners, the exact terminalizer set with
its publication-precondition and handoff-refusal requirements, the single
containment routine, the exact set of public entries that can reach that
routine and the authority each validates first, the protocol-equals-call-shapes
rule for the coordinator seam (including `recover_migration`), and the absence
of conditional branch directives in this Python-only edit boundary.

## Atomic-owner size decision

The split-files guidance was applied again. `lifetime_reference.py` grew from
1,780 to 2,009 lines in correction 1 and to 2,074 lines in correction 2 (the
runtime-open guard, the cleanup claim, the validate-before-commit close
ordering, the late-stop replay and the `admission_state` observer, less the
removed `_revoke_worker_authorization`). The growth is the publication
precondition, the one containment routine that replaced four scattered writers
(`_cancel_or_remove`, the barrier handler, the queue-target handler and the
hard-fence branch), the §8 phase-one entry, the retention indexes and their
discard at terminalization, and the closed observers. Every one of these
touches the same lease owner, command ledger, generation charge and
publication record, so moving any of them behind another object would create
the second mutable owner the accepted design forbids and would make the
rollback and interleaving reasoning cyclic. The file therefore remains the one
recorded atomic-state exception; the buffer and generation modules remain
cohesive subledgers with no independent lease terminalizer. Revisit only when
an accepted design supplies an equally atomic ownership boundary; line count
alone is not authority to fragment this state machine.

## Interpretations recorded for review

- The recorded delivery non-success cause is the triggering registry-owned
  record: the lifecycle observation for task loss, the exit receipt created by
  worker failure, cleanup failure or queue removal, and a registry-issued
  closed failure for barrier failure, fence, revocation or receiver cancel after
  acceptance. Exact replay presents that record; any other record conflicts.
- A usable refresh candidate presented before every scheduled slot is accepted
  is a presentation-only `RefreshCommitRefused` (nothing is invalidated); a
  candidate made unusable while its worker may resume is disposed to
  `RefreshContainmentPending` regardless of the schedule state.
- Terminal success is recorded only by a publication barrier, so generic
  `complete(lease, owner, SUCCEEDED)` on unpublished work refuses as an outcome
  conflict and is otherwise an idempotent replay.
- A retired registration keeps a constant-size tombstone (state and cursors)
  so typed `RefetchRequired` and delivered-progress reporting remain exact; its
  lineage, replay ring and buffer records are discarded.
- `first_lifetime_open` records the lifetime handshake only; the first
  `join_runtime` performs `ACTIVE_UNUSED -> ACTIVE`, so unused withdrawal stays
  available until a runtime has joined.
- Outer terminal-lease records, lifecycle observations and retirement records
  are retained for exact replay; the accepted design sets no bound on them.
- `close_outcome` establishes the coordinator precondition by performing the
  witness (or `close_unjoined`) before its first local mutation; in this
  single-threaded reference that is the validate-then-commit ordering, and an
  injected witness refusal leaves resources, admissions and membership
  unchanged. A cleanup step is claimed when its validation passes, so a
  raising action has still consumed its step and a same-step re-entry is a
  step-unavailable refusal while a next-step re-entry is an in-progress
  refusal.
- IR27 (the post-acceptance cancel/task-loss return value is the accepted
  command's SUCCESS receipt) and IR28 (close, barrier and revocation scans over
  retained outer records) are deferred to W3 by operator decision and are not
  changed here. Design §11's `CURRENT x NONE -> RETIRED x NONE` remains an
  explicit refusal pending decommissioning authority.

## Reference limits and pending gates

This is deterministic single-process contract evidence. It is not thread-safe
or crash-safe and implements no production planner/lowerer, backend adapter,
async/thread/process executor, database durability, migration lock, activation
fence, credentials, service, generator or bytecode artifact. Setup observations
and fixed hostile actions exercise ordering but do not prove physical stop,
durable request release, provenance or cross-process exclusion. SQLite
`ResourceWarning` output is inherited evidence, not suppressed. The call-event
counter used for the retention bound measures Python-level work in this
reference, not production cost.

Round-3 full Code and State review, the re-verdicts of ReviewCode-2,
ReviewState-2, OriginCodeClosure-1-Reverdict, OriginStateClosure-1-Reverdict and
ReviewCode-1-Reverdict on their open findings, manager guard/inventory
verification and a new exact source tuple (MANIFEST-3) remain mandatory; no
further correction is allowed after correction 2. W3 Surface, real
executor/backend behavior, PostgreSQL evidence, SQLite supported-version
behavior, crash recovery and final P12 remain separate future gates. IR20
(`tools/check.py` G10 on `semantic.py`) is outside the write boundary and
remains open.
