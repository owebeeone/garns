# W1/A11 worker-exit contract/reference implementation

**Date:** 2026-10-04  
**Status:** candidate implementation; independent Code/State review and
originating executable closure are pending  
**Authority:** `W1A11-WorkerExitImplementation-ExecutionBrief.md` and the
accepted worker-exit design/acceptance tuple named there

This document records the enacted deterministic contract/reference object. It
does not accept A16, close a finding, authorize a production runtime, or alter
the stopped source/design histories.

## Enacted ownership and type inventory

`ReferenceLifetimeRegistry` is the sole mutable owner of operation leases,
finite command schedules, ordered command ledgers/tombstones, the active command
serial, worker authorization, effect reservation, primary exit and cleanup
diagnostics, receiving-task lifecycle, result escrow/acceptance, containment,
delivery publication/retirement, current refresh candidates and terminal
release. `ReferenceBufferRegistry` is its transactional FIFO/lineage subledger;
it never releases a generation permit. `ReferenceGenerationCoordinator`
continues to own deployment permits, activation-bracketed membership and the
migration attempt phase/request product. `WorkerAuthorizationIssuer` contains
only three delegation callables and owns no record table.

The enacted sealed empty identities are:

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
`MigrationParticipant` is a compatibility alias of `ParticipantMembership`,
not a second identity or state owner.

The principal enacted transitions are `open_lifetime`, `dispatch_worker`,
`dequeue_worker`, `run_worker_effect`, `worker_exit_success`,
`worker_exit_failure`, `request_worker_cancel`, `observe_worker_stopped`,
`observe_receiving_task_done`, `accept_worker_result`,
`prepare_delivery_publication`, `settle_delivery_success`,
`begin_delivery_non_success`, `observe_delivery_stopped`,
`settle_delivery_non_success`, `commit_refresh`, `replay_neutral`,
`settle_contained_refresh`, `join_runtime`, `request_leave`, `finalize_leave`,
`observe_request_released`, and `reopen_no_effect`.

Fixed `command_schedule_provider`, `assigned_worker_provider`,
`effect_provider`, and `cleanup_provider` values are installed only at trusted
reference setup. Per-invocation worker entries accept no effect callback,
worker/task identity, stop boolean, containment owner or caller-composed proof.

## Exact accepted supersession map

| Accepted or historical clause | Enacted additive disposition |
|---|---|
| Overlay §4 worker-to-runtime/containment compare-and-transfer | Exact command exit, receiving task, containment owner, stop observation, receiver acceptance and operation-specific publication now form the transfer. |
| Overlay §4 `PUBLISHING` then separately releasing completion | Non-delivery publication atomically publishes, terminalizes and releases; iterator handoff uses only its specialized atomic success settlement. |
| Overlay §3.2 task disappearance | Exact lifecycle observation invalidates the original context, removes queued work or contains every later prepublication state without receiver resumption. |
| Overlay §5.1 one dispatch/effect ordinal | One finite operation schedule owns distinct command records/tombstones, one active serial and reserve-before-invoke nonreentrant effects. |
| Overlay §§6--7 quiescence | Exact executor-issued stop is required; return, exception, cancellation, cleanup/finally and known result do not establish stop. |
| Overlay §8.2 participant lifetime | Construction is `UNJOINED`; exact open joins; leave is obligation- and frozen-attempt-bound; final idle leave removes later topology obligation. |
| Overlay §9 / A6 neutral progress | `Q`, `C=Q+1`, `R=C`, coalesced neutral spans, current charged candidates and bounded replay make neutral commit terminal and bounded. |
| Overlay §3.1 / §8.2 migration edge | Only the exact current `MIGRATING × MIGRATING_PRE_EFFECT` phase/request/successor proof may reopen old/current; `EFFECT_BEGUN` disables it. |
| Stopped per-call effect callback seam | Replaced by issuer-owned closed commands and fixed setup actions; ordinary effect invocation is `(authorization, ordinal)`. |
| Stopped frontier plus active-head buffering | Replaced by outcome-sensitive FIFO success settlement and two-phase registration retirement/refetch with bounded neutral lineage. |

All other accepted W1/W2 truths remain unchanged: raw `Plan` is absent from
execution protocols; result roles and five result vectors remain intact;
parameters/binding/generation/ancestry/kind remain pinned; derived commands have
no independent permit; public context remains empty and task-bound; A7 outcome
knowledge remains independent; local close remains distinct from migration.

## Executable regression disposition

The existing suites retain the original admission, result-role, lifetime,
generation and product attacks. The seven historical
`test_worker_authority.py` tests were adapted into six stronger grammar-level
tests rather than dropped:

| Historical attack | Retained executable coverage |
|---|---|
| empty handle/task-bound context | `test_private_handles_are_empty_exact_and_nontransferable`; existing authority tests |
| consume ordinal before one effect | `test_effect_api_has_no_callback_or_caller_identity_and_reserves_once` |
| wrong tuple has zero effect | `test_wrong_worker_and_lifecycle_identities_are_mutation_free`; `test_worker_entries_have_no_callback_or_caller_identity_override` |
| atomic dequeue tuple | same wrong-worker test plus exact dequeue in every worker causal trace |
| issuing task cannot impersonate worker | wrong-worker test and worker-source validation in the effect tests |
| expiry/invalidation/revocation | retained lifetime revocation matrix and `test_precommit_expiry_fence_and_migration_all_retire_the_active_head` |
| hard fence retains charge | `test_baseexception_contains_before_escape_and_revokes_unused_effect`, retained hard-fence lifetime test, and stop-gated delivery/refresh tests |

The baseline focused count was 97. The adapted pre-new-file suite is 96 only
because those seven overlapping worker tests became six; the attack mapping
above preserves their causal content. The dedicated worker-exit file adds 27
stateful tests and the source-rule file adds 7, for 130 focused tests.

The five stopped roots and later residuals map as follows:

| Root / retained IDs | Stateful regression locations |
|---|---|
| Worker exit (`ReviewState-3 P2-1`, `Consistency-1 P2-2/P2-3`, `Safety-1 P2-1`) | `test_worker_authority.py`; `WorkerExitCausalTests`: finite C1/C2 ledger, reserve/reentrancy/BaseException, cleanup winners/order, queue removal, stop-before-accept, atomic generic publication, task loss at every pause and identity attacks. |
| Failed FIFO (`ReviewCode-3 P2-1`, `ReviewState-3 P2-2`, `FreshCodeClosure-2 P2-1`, `Safety-2 P2-1`) | delivery success, first-head failure with successor invalidation, receiver loss, precommit expiry/fence/migration, commit-first late barriers, plus retained two-head success/invalidation/close tests. |
| Participant lifecycle (`ReviewCode-3 P2-2`) | unjoined admission/close, pending leave in frozen attempt, later-attempt absence, copy/cross/stale membership, and join-during-drain refusal. |
| Neutral refresh (`ReviewState-3 P2-3`, `Consistency-1 P2-4`, `Safety-1 P2-2`, `Consistency-2 P2-1/P2-2`) | zero-queue atomic neutral, delayed changed head/span fold, more-than-`R` replay eviction, active+`Q` overflow, changed-neutral-changed gaps, and nonquiescent known-candidate stop settlement. |
| Phase proof (`OriginStateClosure-1/2 State-Closure-P2-1`, `Consistency-1 P2-1`) | stale same-attempt drain proof, exact current pre-effect proof, effect-begun refusal, exact serial/request transitions, wrong request and replay/cross proof tests. |

Initial-18 and correction-1 13/F1--F10 coverage remains distributed through
`test_result_roles.py`, `test_admission_contracts.py`,
`test_lifetime_contracts.py`, `test_worker_authority.py`,
`test_generation_contracts.py`, and `test_contracts.py`. In particular F1 is
the issuer-owned `ClosedPlanConsumer`/source rule; F2 is atomic publication;
F3/F4 are pinned detached inputs and parent-owned derived commands; F5/F6 are
authority/generation/resource revalidation; F7 is exact current-worker
authentication; F8 is stop-gated containment and receiver loss; F9 is exact
successor/phase proof; F10 is exact queue ancestry/state revalidation. The five
accepted result vectors remain in `test_result_roles.py`.

`test_contract_source_rules.py` parses every owned Python contract source and
checks the no-raw-`Plan` protocol boundary, worker entry signatures, stateless
worker façade, centralized shared-permit release, single cursor/membership/
proof-construction owners, specialized delivery terminalizers, and absence of
conditional branch directives in this Python-only edit boundary.

## Atomic-owner size decision

The split-files skill was applied. `lifetime_reference.py` grew from the
brief's 796-line exception to 1,780 lines. It remains one explicit exception
because splitting its worker authorization, lease owner, current refresh
candidate, delivery settlement or terminal release would create the secondary
mutable owner the accepted design forbids. The buffer and generation modules
remain cohesive subledgers with no independent lease terminalizer. Revisit
only after a later accepted design supplies an equally atomic ownership
boundary; line count alone is not authority to fragment this state machine.

## Reference limits and pending gates

This is deterministic single-process contract evidence. It is not thread-safe
or crash-safe and implements no production planner/lowerer, backend adapter,
async/thread/process executor, database durability, migration lock, activation
fence, credentials, service, generator or bytecode artifact. Setup observations
and fixed hostile actions exercise ordering but do not prove physical stop,
durable request release, provenance or cross-process exclusion. SQLite
`ResourceWarning` output is inherited evidence, not suppressed.

Independent full Code and State review, the two originating executable closure
runs, manager guard/inventory verification and a new exact source tuple remain
mandatory. W3 Surface, real executor/backend behavior, PostgreSQL evidence,
SQLite supported-version behavior, crash recovery and final P12 remain
separate future gates.
