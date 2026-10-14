# W1A11-WorkerExitImplementation (originating executable closure) — CODE-AXIS REVIEW

**Review object:** The candidate worker-exit internal contracts/reference implementation, compared with the archived 20-file baseline. It is the approved filesystem tuple `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`, SHA-256 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` (117 entries). This is not a Git commit. The controlling DRAFT is `dev-docs/W1A11-WorkerExitImplementation-DRAFT.md` at `e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`. Status: unaccepted candidate, builder writes stopped. Reviewed 2026-10-04. To be filed as `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1.md`.
**Baseline:** Approved no-Git filesystem-SHA tuple. All sources were read directly from `/Volumes/projects/limbo/garns-wz/garns`, not from Git HEAD. That tree is the byte-exact 2026-10-04 relocation of `/Volumes/projects/limbo/datascad/garns-v9-6`; the DRAFT's links to the old path refer to the same bytes. The comparison object is the archived originals under `dev-docs/W1A11-WorkerExitImplementation-Baseline/` (map `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a`, 20 entries). The stopped 71-file source survives only as evidence, through the rebased Legacy maps.
**Date:** 2026-10-04
**Axis:** Code. This is the originating executable closure of `ReviewCode-3 P2-1` (failed-FIFO accounting) and `ReviewCode-3 P2-2` (activation-bracketed participant lifecycle) on actual model transitions. It covers interface contracts against call sites, error paths, and DRAFT-versus-bytes conformance, and it retraces the initial-18 and F1–F10 obligations where the assigned paths touch them. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO.** Seven P2 findings block: two residuals of `ReviewCode-3 P2-2` and five new bounded roots. Three P3 findings do not block. The original `ReviewCode-3 P2-1` counterexample is executably closed. `ReviewCode-3 P2-2` is only partially closed: the original reproductions A and B are closed, but two residuals of its required correction remain. No finding requires a change to the accepted design, architecture, ownership boundary or compatibility decision; every blocker is a bounded source correction. I pre-commit to GO on a revision that resolves P2-1, P2-2, P2-3, P2-4, P2-5, P2-6 and P2-7 as specified.

---

## Replacement and model disclosure

- **Fresh replacement.** The original Code reviewer context for this lane ran in another harness and did not survive the handoff. I am a fresh Claude subagent dispatched with model parameter `opus`. The prompt records `gpt-5.6-sol high` as the model originally selected for this lane; the operator directed this round to Claude reviewers.
- **No inherited state.** I relied on no prior agent memory. All evidence below was reconstructed from the filed documents and from commands I ran.
- **Prior reports are inputs, not proof.** The earlier `ReviewCode-3` and `OriginCodeClosure-3` (+ Erratum) were read as filed testimony and re-tested executably, not taken as proof.
- **F8 context.** I treat the earlier lost F8 context as a fresh replacement after material design change, as the prompt states. F8 vectors are retraced below only where they touch these paths; I claim no intact origin for them.

## Prior-finding closure table (original IDs)

| Original ID | Prior status | Re-run on this tuple through the exact replacement path | Status |
|---|---|---|---|
| `ReviewCode-3 P2-1`: refusing an unpublished head advances `delivered_through` and exposes the successor | Source OPEN; design closure prospective only (`OriginCodeClosure-3`) | Two ranges `(0,1]`, `(1,2]`, then the head fails before publication, under each cause: direct worker failure, cancellation, cleanup failure, authority expiry, receiver loss, hard fence, graceful close and migration. The removed generic entry points (`complete(..., REFUSED)`, `complete_contained`) refuse on a handoff without mutation. In every cause:<br>• delivered stays 0;<br>• the successor dequeue refuses `refetch_required`;<br>• the queued permit is released exactly once (count 2→1);<br>• the active charge persists until exact worker and delivery stop;<br>• specialized settlement releases once (count 0) and returns `RefetchRequired`;<br>• replay is read-only.<br>Migration stays blocked (`deadline_exceeded`) while the head is retained and proceeds only after settlement. The old registration refuses; recovery works only through a new registration. On the last-permit success path, commit-first is atomic and every barrier-first race retires. | **CLOSED (executable)** for the original counterexample and every closure vector on single-command deliveries. Two separate new roots remain in the same settlement/recovery neighbourhood: **P2-1** breaks phase-2 conservation for multi-command deliveries, and **P2-7** affects refetch-baseline publication. Neither is a regression of the original sequence. |
| `ReviewCode-3 P2-2`: constructor-time membership allows preactivation authority; no quiescent final leave | Source OPEN; design closure prospective only | **Repro A:** construction while unactivated yields no membership; admission and join refuse `activation_required`; no preactivation handle exists. **Repro B:** two participants; one fully closes and becomes `left`; a later attempt freezes only the live member, and migration proceeds on its acknowledgement alone. Copy, counterfeit and cross-coordinator tokens refuse. Unregister while a live operation exists refuses. Join during an attempt refuses; leave during an attempt keeps the frozen set and the member becomes `left` after cutover. | **PARTIALLY CLOSED → OPEN.** Repros A and B are closed. Two halves of the required correction remain open: **P2-2** (leave finalization uses an incomplete obligation predicate) and **P2-3** (the formal protocol still lacks the join/leave pair). |

## Changed-range analysis

I diffed all 20 archived originals against the live tree.

- **Byte-identical (5, by `cmp`):** `authority.py`, `consumers.py`, `lifetime.py`, `protocols.py`, `__init__.py`.
- **Changed (15):**
  - `admission.py` (+2 lease states);
  - `worker_authority.py` (rewritten to empty identities plus a stateless façade, 223→143 lines);
  - `lifetime_reference.py` (796→1,780 lines);
  - `buffer_reference.py` (333→502);
  - `snapshot_reference.py` (+neutral receipt, `take_refresh`);
  - `generation_reference.py` (440→561);
  - `migration_reference.py` (111→127);
  - `values.py` (+three refresh result types and codes);
  - five retained test files;
  - A16 and the ADR README.
- **Added (3):** `test_worker_exit_contracts.py` (841 lines), `test_contract_source_rules.py` (187 lines), `W1A11-WorkerExitImplementation.md`.
- **Retained tests:** attacks were adapted to the replacement entry points, not removed. For example, `dispatch_to_worker`/`cancel_queued` became `dispatch_worker`/`request_worker_cancel`, `setup_reference_no_effect_proof` became `observe_request_released`, and generic handoff completion became `settle_handoff`/`retire_handoff`.

Where each finding sits in the changed range:

- **New code:** P2-1 (`dispatch_worker`), P2-4 (`run_worker_cleanup`), P2-5 (generic publication and refresh commit lack the ledger guard used by the delivery path), P2-6 (new sole internal entry `commit_refresh`).
- **New membership code:** P2-2.
- **Unchanged file, required change missing:** P2-3 (`lifetime.py:262-281`).
- **Baseline grammar retained, contrary to accepted §2:** P2-7. The pattern exists at baseline `lifetime_reference.py:495-501` and is now reachable through this build's new task-loss and cancel entries.
- **Shape deviations:** P3-1 (first open is not atomic with join).
- **Coverage:** P3-2 (replay identity), P3-3 (source-rule enumeration).

Where the bytes do not do what the DRAFT and implementation record claim:

- "two-phase non-success retirement" fails for multi-command handoffs (P2-1).
- "obligation-bound leave" is incomplete (P2-2).
- "retryable `RefreshCommitRefused`" holds only on `publish_refresh_buffer`, not on `commit_refresh` (P2-6).
- "exact stop-before-accept" does not gate generic publication (P2-5).
- The record's supersession row "Non-delivery publication atomically publishes, terminalizes and releases" is false for snapshot registration (P2-7).

**Classification.** No new root changes ownership: the lifetime registry remains the sole lease/worker owner and the coordinator remains the deployment and membership domain. All seven blockers are bounded and none is architectural, so the source two-correction cap is not triggered. The implementation correction count remains zero until the manager remediates.

## 0. Evidence base

**Authority and controls read completely**
- My prompt; SHA-256 re-verified `5f5226af…ce9` at start and end.
- The review-loop `SKILL.md` and its canonical `references/review-prompt-template.md`.
- `../AGENTS_GWZ.md` and product `AGENTS.md`.
- Program plan §§15–18 (lines 767–859).
- The ExecutionBrief, the DRAFT and the implementation record.
- `Verification-1`. For `VerificationLogs-1` I read the header only and reproduced every gate myself.
- The accepted design `W1A11-WorkerExitRedesign.md` (all 1,121 lines) and its ACCEPTANCE.
- `W1-ACCEPTANCE`, `W2-QueryPlanningDesign` (complete), `W2-AdmissionLifetimeRedesign` (complete) and its ACCEPTANCE.
- `docs/PRODUCT_LAYOUT.md`, `docs/adr/A16-admission-lifetime.md` and `docs/adr/README.md`.
- The stopped-source and design reports named by Inputs: `ContractAmendment-STOP`, `ReviewCode-3`, `ReviewState-3`, `FreshCodeClosure-2`, `OriginStateClosure-2`, `RemPlan`, `RemPlan-2`, `WorkerExitRedesign-ReviewConsistency-3`, `ReviewSafety-3`, `OriginCodeClosure-3` plus Erratum, and `OriginStateClosure-3`.
- Hash maps were verified by content. `Inputs`, `Baseline` and `MANIFEST-1` were also read line by line.

**Not read:** the Handoff and HandoffEvidence (out-of-scope manager artifacts); RelocationEvidence; any Prompt-1 file or any other Prompt-2. No current-round review or closure report existed in `dev-docs/` during the review.

**Source read completely:** `lifetime_reference.py` (1,780 lines), `generation_reference.py`, `migration_reference.py`, `buffer_reference.py`, `worker_authority.py`, `admission.py`, `lifetime.py` and `authority.py`.
**Read by diff:** `snapshot_reference.py`, `values.py`, and the retained-test diffs.
**Tests read completely:** `test_worker_exit_contracts.py` and `test_contract_source_rules.py`. From the retained suites I read the fixture helpers (`build_fixture`, `make_lifetime_fixture`, `register`, `publish`, `settle_handoff`, `retire_handoff`) and the retained-test diffs.

**Tuple verification at START and END (identical both times)**

| Check | Result |
|---|---|
| `shasum -a 256 MANIFEST-1` | `7e80ca67…ea544` |
| `shasum -a 256 -c MANIFEST-1` | 117/117 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 OK |
| `WorkerExitRedesign-AcceptanceEvidence` | 13 OK |
| DRAFT SHA-256 | `e8e2f73e…57ff2` |
| `.pyc` / `.pyo` / `__pycache__` | 0 |

**Gates.** Each was run with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb` and `-B`, with no warning filters.

```text
[3.11.14 focused] rc=0 :: Ran 130 tests in 0.207s OK
[3.12.12 focused] rc=0 :: Ran 130 tests in 0.137s OK
[3.13.12 focused] rc=0 :: Ran 130 tests in 0.211s OK
[3.14.3 focused] rc=0 :: Ran 130 tests in 0.151s OK
[3.11.14 full] rc=0 ResourceWarning-lines=0 :: Ran 233 tests in 18.449s OK
[3.12.12 full] rc=0 ResourceWarning-lines=0 :: Ran 233 tests in 13.560s OK
[3.13.12 full] rc=0 ResourceWarning-lines=114 :: Ran 233 tests in 1.675s OK
[3.14.3 full] rc=0 ResourceWarning-lines=136 :: Ran 233 tests in 1.522s OK
tools/check_product.py (all four): PASS product paths / pinned baseline inputs / cache hygiene / shipped path hygiene / W0 product baseline
```

The inherited SQLite ResourceWarnings stayed visible on 3.13 and 3.14. `tools/check.py` was not run.

**Probes.** All attacks were inline `-B` stdin Python on 3.14.3, driving the real reference transitions through the repository's own test fixtures. The fixture's trusted providers (current task, clock, schedule, worker, effect and cleanup providers) were used exactly as the builder's tests use them. Private fields were read only for observation (`_leases[...]`, `_attempts[...].required`, `_participants`, `_join_serial`, `_buffers.registration_state`, `_admissions`) and were never assigned.

**Procedural notes**
- One command redirected the START `shasum -c MANIFEST-1` output into the session scratchpad (`/private/tmp/claude-501/…/scratchpad/start_manifest.txt`), outside the product tree. After that, every output was piped. The tuple was unchanged at END.
- No helper agents, Git/GWZ operations, network, services, installs, compileall or `py_compile` were used.

## 1. Findings

### [P2-1] `dispatch_worker` dispatches later schedule slots without validating the outer lease, resurrecting contained operations and stranding retiring deliveries

**Classification:** new root; bounded code correction; no accepted-design change.

**Location:** `src/garns/backends/contracts/lifetime_reference.py:458-492`.
- For serial > 1, the only precondition is `prior.state is RESULT_ACCEPTED` (lines 467-470).
- The outer-state check at 471-472 applies only to serial 1.
- Lines 490-491 then unconditionally assign `record.owner = command` and `record.state = LeaseState.QUEUED`.

**Violated invariant (accepted design):**
- §4.2: dispatch requires "the immediately preceding record at `RESULT_ACCEPTED` under the exact runtime-continuation owner"; "A contained command ends the operation schedule; no later slot may dispatch."
- §4.1: "no edge back to a worker-owned state."
- §5.2: a post-acceptance cancel "moves the already-quiescent outer lease to containment without reopening the command."
- §8: phase 1 "revokes remaining worker/iterator authority."

**Reproduction:** a two-slot trusted schedule (`WorkerCommandSpec("c1",(1,)), WorkerCommandSpec("c2",(1,))`).
- (a) EXECUTE: C1 is accepted. The receiving task calls `request_worker_cancel` and then `dispatch_worker`; C2 runs and the operation publishes.
- (b) ITERATOR_HANDOFF over `(0,1]`, `(1,2]`: C1 is accepted. The coordinator runs `begin_drain` and `migration_queue_barrier`, retiring the handoff. Then the continuation dispatches C2.

```text
N1 after receiver cancel: contained | owner is containment: True
N1 dispatch C2 after cancel: ACCEPTED -> queued | owner is containment: False
N1 cancelled operation then publishes: succeeded publications 1 count 0
N2 retired by barrier: retiring_handoff count 1
N2 dispatch C2 on retiring delivery: ACCEPTED -> queued
N2 after C2: publication_ready | success: refused:operation_outcome_conflict
N2 specialized non-success settle: refused:lease_invalid | complete_contained: refused:operation_outcome_conflict | complete: refused:lease_owner_conflict
N2 replay begin: True -> state publication_ready | count 1
N2 migration: refused:deadline_exceeded | close outcome: nonquiescent
```

**Impact:**
- The containment owner's claim is overwritten, and a cancelled operation executes effects and publishes `SUCCEEDED`.
- A retiring delivery runs effects after its authority should have been revoked, during `DRAINING_OLD`.
- Afterwards no edge returns to `RETIRING_HANDOFF`, so §8 phase 2 is unreachable. The charge is stranded permanently, deployment migration and runtime close can never complete, and the conservation that closes `ReviewCode-3 P2-1` fails for multi-command deliveries.
- Severity is P2 rather than P1, following this lane's precedent for permanent drain or migration blocks (`ReviewCode-3 P2-2`).

**Required correction:** before any mutation, for every serial:
- the lease is non-terminal and not `CONTAINED`, `RETIRING_HANDOFF`, `PUBLICATION_READY` or `PUBLISHING`;
- no delivery retirement, candidate or settlement exists;
- serial 1 requires `ACQUIRED`/`RUNNING` under the current caller owner;
- serial > 1 requires `RUNNING` with `record.owner is record.continuation_owner` and a live receiver;
- otherwise, refuse without mutation.

**Closure test:**
- M=2 EXECUTE: accept C1, cancel, then dispatch C2. The dispatch must refuse with state, owner, ledger, count and publications unchanged. `complete_contained` then yields `REFUSED` with count 0.
- M=2 delivery: retire after C1 acceptance via migration barrier, close, fence, overflow and receiver loss. Dispatch of C2 must refuse without mutation each time. Stop plus specialized settlement then releases once, and migration proceeds.

### [P2-2] Final leave is decided by the coordinator from generation permits alone, not from the runtime's quiescent local close

**Classification:** residual of `ReviewCode-3 P2-2`. Its required correction reads: "Final `CLOSED` transition must unregister the exact participant only after all retained permits, handoffs, and close work are terminal." Bounded.

**Location:**
- `generation_reference.py:130-144`: `request_leave` has no precondition; `finalize_leave` checks only that no attempt is open and `_runtime_has_obligations`.
- `generation_reference.py:516-517`: that predicate covers only generation permits whose operation carries the member's runtime identity.
- `generation_reference.py:525-528`: `_finish_pending_leaves` applies the same predicate at every attempt close.
- `generation_reference.py:223-236`: `acquire_shared` ignores membership.
- `lifetime_reference.py:236-238`: the membership token is exposed publicly.
- `lifetime_reference.py:278-279`: `_admit` checks only `_membership is None`.
- `lifetime_reference.py:1430-1438`: `close_outcome` closes irreversibly and only then calls a finalize that can refuse.

**Violated invariant (accepted §9 and brief):**
- `finalize_leave` may remove a member only when the runtime is `LOCAL_CLOSED` and has no operation or generation permit, queued or active delivery, worker or containment record, registration-close work, or unresolved close obligation including A7 identities.
- "a quiescent `LEAVE_PENDING` member becomes `LEFT`."
- "Admission records and leases bind the exact membership and join serial."
- Every refusal must leave membership and migration state unchanged.

**Reproduction:**
- (a) Registry-only path. `start_close(runtime)`, then `close_outcome(runtime,(tx,))` reports UNRESOLVED. Then drain, barrier, `observe_request_released` and `reopen_no_effect`.
- (b) Public token path. The runtime is `LOCAL_OPEN` with one queued delivery permit. `coordinator.request_leave(registry.membership)` is followed by `finalize_leave`.
- (c) Close during a frozen attempt.

```text
O2 unresolved A7 (registry path): unresolved leave_pending
O3 after no-effect reopen while UNRESOLVED: left | runtime local state: local_draining | A7 still unresolved: unresolved
O4 later attempt includes the unresolved runtime: False | required size: 0
pre: count 1 runtime local_open membership joined
request_leave: leave_pending | finalize_leave: ACCEPTED -> left
LEFT runtime still acquires a new permit: acquired count 2
frozen attempt omits the open runtime: True | its barrier: refused:migration_indeterminate
begin_migration: refused:deadline_exceeded | count (queued permit no participant can invalidate): 1
close_outcome during attempt: raised lease_invalid | runtime local_closed | admissions ['retired'] | membership leave_pending
repeat close_outcome during attempt: raised lease_invalid
```

**Impact:**
- Membership is removed while close obligations remain: an unresolved A7 identity, a runtime that is not closed, a queued delivery.
- A live runtime keeps acquiring work while absent from frozen topology. Migration then either blocks on a queued permit no participant can invalidate, or freezes an empty participant set.
- Close during an attempt reports a refusal after irreversibly closing local resources.

**Required correction:** make final leave one registry-witnessed transition.
- The registry presents an exact sealed close-quiescent record for its membership, and only on a `CLOSED` outcome: `LOCAL_CLOSED`, no non-terminal operation, no queued or active delivery, no unresolved identity.
- The coordinator records it. During an attempt it does so without mutating the frozen set, and finalizes `LEFT` immediately when no attempt is open, otherwise at attempt close.
- `finalize_leave` and `_finish_pending_leaves` require that record.
- `request_leave` requires the registry's drain fence.
- Admissions and leases bind membership and join serial, and refuse after `LEFT`.
- `close_outcome` returns `CLOSED` without raising.

**Closure test:**
- (a) The UNRESOLVED runtime stays `LEAVE_PENDING` across reopen, cutover and recovery until its `CLOSED` outcome, and the next attempt still includes it.
- (b) Direct finalize of an open runtime holding a queued permit refuses with membership, count and queue unchanged; a `LEFT` membership cannot admit or acquire.
- (c) Close during an attempt returns `CLOSED` with membership `LEAVE_PENDING`; the member becomes `LEFT` after the attempt closes and is absent from the next attempt.

### [P2-3] The formal coordinator seam still cannot require the membership lifecycle pair or phase-exact proof

**Classification:** residual of `ReviewCode-3 P2-2`. Its required correction reads: "Add an exact participant join/leave contract to the formal protocol and reference coordinator." Its root cause named `lifetime.py:262-281`. Bounded interface correction.

**Location:**
- `src/garns/backends/contracts/lifetime.py:262-281`, byte-identical to the baseline.
- `begin_migration(...) -> None` is now stale, because the reference allocates a phase request on that transition.
- No source or test file references `SharedGenerationCoordinator` other than its own definition.

**Violated invariant:**
- Accepted §9 call shapes (`join_runtime`, `request_leave`, `finalize_leave`, `close_unjoined`) and §11 calls (`observe_request_released`, `reopen_no_effect`).
- §13 assigns `lifetime.py` the provisional internal seams.
- Review contract: a missing half of a lifecycle pair is a finding.

**Reproduction:**

```text
protocol methods: ['acquire_shared', 'add_buffer', 'begin_drain', 'begin_migration', 'count', 'mark_indeterminate', 'permit_live', 'publish_generation', 'release_buffer', 'release_shared']
reference-only methods: [... 'close_unjoined', ... 'finalize_leave', ... 'join_runtime', ... 'observe_request_released', ... 'reopen_no_effect', 'request_leave', ...]
coordinator with no join/leave/phase-proof satisfies formal seam: True
```

**Impact:** a W3/W4 coordinator written to the formal seam may omit activation-bracketed membership and phase-exact proof. That reintroduces the `ReviewCode-3 P2-2` and `State-Closure-P2-1` defect classes with no static or runtime conformance failure.

**Required correction:**
- Add the §9 `join_runtime`/`request_leave`/`finalize_leave`/`close_unjoined` set and the §11 proof and effect-begun transitions to the protocol, using exact identity types.
- Correct the `begin_migration` return type.
- Type the registry against the protocol, or add a conformance check.

**Closure test:**
- `ReferenceGenerationCoordinator` satisfies the protocol.
- A stub missing any membership or proof member fails `isinstance`.
- A source rule asserts that the protocol's member set equals the accepted call-shape set.

### [P2-4] `run_worker_cleanup` validates inside its containment scope: a wrong-task refusal contains the command, and in-flight cleanup records `NOT_BEGUN`

**Classification:** new root. It reopens the F9 / `OriginCodeClosure-1 P2-6` zero-mutation property on a new worker entry point. Bounded.

**Location:** `lifetime_reference.py:615-641`.
- The current-worker check (626-627) raises inside `try`.
- `except BaseException` (632-639) then commits a primary FAILURE through `_contain_command(..., command.effect_knowledge, ...)`.
- `finally` (640-641) consumes the cleanup step.
- No state, reservation or active-serial validation happens before the `try`.

**Violated invariant:**
- §7: a wrong current worker gets "refusal before mutation; no effect, ordinal consumption, owner transfer or count change."
- F9 closure: "impersonation yields zero effects, unchanged … owner/state and unconsumed ordinals."
- §4.1: `BEGUN_UNCERTAIN` means a reserved effect had not returned when containment won.
- §4.2: refuse if "the wrapper is already on this command's stack."

**Reproduction:**
- (a) The receiving task, which is not the assigned worker, calls cleanup while the worker is `running_idle`.
- (b) A fixed effect re-enters cleanup while its own ordinal is in flight, and the cleanup raises.

```text
(a) before ('running', 'running_idle', 'not_begun', (1, 2), None, False)
(a) wrong-task cleanup refused:worker_authority_invalid -> after ('contained', 'contained', 'not_begun', (), <WorkerExitKind.FAILURE: 'failure'>, True) next_cleanup_step 2
(a) genuine worker's next effect: refused:worker_authority_invalid
(b) effect 1 outcome: RuntimeError -> facts ('contained', 'contained', 'not_begun', (), <WorkerExitKind.FAILURE: 'failure'>, True) | ordinal 1 completed: False
```

**Impact:**
- Any holder of the authorization can pre-empt the worker. While the call reports a refusal, it has already minted the primary FAILURE receipt, revoked every ordinal and moved ownership to containment.
- Re-entrant cleanup records the false fact that no effect began.

**Required correction:**
- Before the `try`, validate the exact active serial and authorization, the current assigned worker, step order and a legal state (never `EFFECT_IN_FLIGHT` or with an active reservation; §5.3 post-primary rules). Refuse without mutation.
- When cleanup is the primary failure, derive knowledge from the reservation history.

**Closure test:**
- Wrong-task cleanup in `RUNNING_IDLE`, `EFFECT_IN_FLIGHT` and `CONTAINED` refuses with state, owner, ordinals, exit facts and step unchanged; the genuine worker then succeeds.
- Re-entrant cleanup refuses.
- A cleanup-primary after a reserved, unreturned effect records `BEGUN_UNCERTAIN`.

### [P2-5] Non-delivery publication and refresh commit do not require a complete, quiescent command ledger

**Classification:** new root; bounded.

**Location:** `lifetime_reference.py`.
- 372-413: the ledger check (380-388) covers only `ITERATOR_HANDOFF`; EXECUTE and CONSISTENT_SNAPSHOT publication terminalizes at 406-413.
- 980-1057: `_commit_refresh_record` checks only `record.state is RUNNING` (989) before its neutral (1013-1026) and changed (1032-1057) terminal commits.
- By contrast, `complete()` (746-750) treats a non-empty ledger as worker-backed, and `prepare_delivery_publication` (1182-1190) requires the full ledger.
- The shipped default worker provider (214) assigns the receiving task's own identity as the worker.

**Violated invariant:**
- §3: "Every slot is required … no caller may … skip."
- §4.1: "Public publication is legal only after serial M is `RESULT_ACCEPTED`, no command is active."
- §5.1: "Success is not … publishable before stop observation."
- §6: a worker return never releases a permit.
- §10: a refresh whose worker may still resume retains its charge until exact stop.

**Reproduction:**
- (a) An M=2 EXECUTE publishes after C1 alone.
- (b) Under the default provider, publication happens while the command is still running.
- (c) A refresh commit happens while its command is still running, under a distinct worker identity.

```text
(a) M=2 publish after C1 only: ACCEPTED succeeded ledger 1 of 2 count 0
(b) publish while command running_idle : ACCEPTED succeeded count 0 exit None
neutral  distinct worker: commit while running_idle (no exit/stop) -> NeutralRefreshReceipt; lease succeeded; count 0; cursors (1, 1)
changed  distinct worker: commit while running_idle (no exit/stop) -> BufferedDelivery; lease succeeded; count 1; cursors (1, 0)
```

**Impact:**
- Required commands are skipped.
- Operations terminalize and release the generation charge while a worker can still resume, with no exit and no stop.
- Close and migration counts can reach zero while worker execution is live.

**Required correction:** apply one ledger guard on every generic terminal-success path: non-delivery `PUBLICATION`, neutral and changed refresh commit, and snapshot registration (P2-7). When the ledger is non-empty, require no active command, `len(ledger) == len(schedule)` and the last record `RESULT_ACCEPTED` under the continuation owner. Otherwise refuse without mutation, or for a refresh apply §10's nonquiescent containment.

**Closure test:** the three sequences refuse with state, owner, count, cursors and publications unchanged. After every slot is accepted, publication and commit succeed exactly once.

### [P2-6] `commit_refresh` turns a wrong-task presentation of a live candidate into terminal refusal

**Classification:** new root (this build introduced the entry point); bounded.

**Location:** `lifetime_reference.py`.
- 963-972: no presentation check.
- 997-1001: any barrier refusal goes to `_dispose_refresh`, which records terminal `REFUSED` and releases the charge (1110-1116).
- `_validate_barriers` (1496-1529) contains on every refusal, including the `CONTEXT_OWNER_MISMATCH` that `authority.py:62` raises because of the caller's task.
- The build's own `RefreshCommitRefused` docstring says "Presentation-only refusal; the live charged candidate remains current."

**Violated invariant (§10):**
- "A presentation-only mismatch that does not invalidate the recorded operation returns `RefreshCommitRefused` with candidate, owner, lease and charge unchanged, so only the original authority can retry."
- "A known current candidate presented under a wrong lease/authority refuses with its original owner and charge unchanged."

**Reproduction:**

```text
changed  before=('running', 1, 1, (0, 0)) wrong-task-> RefetchRequired after=('refused', 0, 0, (0, 0)) | owner retry -> RefreshRecordUnavailable
neutral  before=('running', 1, 1, (0, 0)) wrong-task-> RefetchRequired after=('refused', 0, 0, (0, 0)) | owner retry -> RefreshRecordUnavailable
```

**Impact:**
- Any task that obtains the opaque candidate can destroy another task's live refresh, forcing a refetch and releasing its charge; the legitimate authority loses the operation.
- The DRAFT's "retryable wrong-owner presentation" is true only for `publish_refresh_buffer`.

**Required correction:**
- Establish presentation authority before validating barriers: the current task must be the lease's recorded receiving task / context owner. On mismatch, return `RefreshCommitRefused` without mutation.
- Keep the containment and terminal dispositions for genuine invalidation only: expiry, invalidation, fence, generation, cursor divergence, retirement, overflow.

**Closure test:**
- A wrong-task `commit_refresh` of changed and neutral candidates returns `RefreshCommitRefused` with state, candidate count, coordinator count and cursors unchanged; the owner's retry then commits exactly once.
- Expiry and fence still follow §10.

### [P2-7] Snapshot registration publishes before terminal success and keeps a separately callable releasing completion

**Classification:** retained superseded grammar (present at baseline lines 495-501), now reachable through this build's receiver-loss and cancel entries; bounded.

**Location:**
- `lifetime_reference.py:851-896`: publication and registration are recorded and returned at 890-896 while the lease stays `PUBLISHING` and keeps its permit.
- `complete()` 751-760 performs `PUBLISHING → SUCCEEDED` as a separate call.
- `_cancel_or_remove` 1646-1651 followed by `complete_contained` 762-775 relabels the operation.
- The fixture `tests/contracts/test_lifetime_contracts.py:102-103` depends on the separate completion.

**Violated invariant:**
- Accepted §2, row 2: `PUBLISHING` is "a nonterminal precommit state, not a separately released outcome … Neither operation kind has a separately callable releasing completion after publication."
- §5.2: after publication, task loss "cannot relabel success."
- §8: "Refusal leaves no usable new registration."

**Reproduction:**

```text
receiver_loss   after publication=('publishing', 1, 1) -> terminal=('refused', 0, 'active') | registration of the refused operation still delivers: cursors (1, 1)
receiver_cancel after publication=('publishing', 1, 1) -> terminal=('refused', 0, 'active') | registration of the refused operation still delivers: cursors (1, 1)
```

**Impact:**
- The terminal outcome contradicts published state.
- The refetch recovery that closes `ReviewCode-3 P2-1` can yield a "refused" baseline whose registration is still live. A retrying caller then creates a second live lineage for the same subscription.

**Required correction:**
- Make `register_subscription` one atomic commit: publication, registration, terminal `SUCCEEDED` and release, all before returning.
- Drop the separate completion from the fixtures.

**Closure test:**
- After registration the lease is `SUCCEEDED` with its permit released; a later receiver loss or cancel is a no-op.
- A failure before the commit leaves no usable registration and exposes no rows.

### [P3-1] First open and join are separate; `first_lifetime_open` is not bound to any runtime open

**Location:**
- `generation_reference.py:101-120`: join refuses unless `ACTIVE` (line 107).
- `generation_reference.py:198-203`: `first_lifetime_open(protocol, epoch)` performs `ACTIVE_UNUSED → ACTIVE` without an open record or membership issuance.

**Violated invariant:** §9 says `join_runtime` validates "`ACTIVE_UNUSED(epoch)`/first-open or `ACTIVE(epoch)` … First open changes `ACTIVE_UNUSED` to `ACTIVE` in the same transaction." Under overlay §8.1, unused withdrawal is allowed while no lifetime runtime ever opened.

**Reproduction:**

```text
after first open with no runtime: activation active | participants 0 | joins issued 0
withdraw with exact fence and no runtime ever joined: refused:activation_required
```

**Impact:** the irreversible activation edge can be taken with zero participants, and the right to withdraw an unused activation is lost. Because `ReviewCode-3 P2-2` explicitly allowed refusing pre-fence join as an alternative, this does not keep P2-2 open; it is a deviation from the accepted §9 shape.

**Remedy:** `join_runtime` accepts `ACTIVE_UNUSED` with matching protocol and epoch and performs first open in the same mutation; retire or bind the standalone call.

**Closure test:** first join in `ACTIVE_UNUSED` atomically yields `ACTIVE` plus a membership; first open without an open record refuses; withdrawal remains available until the first join.

### [P3-2] Replay paths accept non-identical inputs as exact replay

**Location:** `lifetime_reference.py:599-602` (`worker_exit_failure`) and `1244-1245` (`begin_delivery_non_success`).

**Violated invariant:**
- §6: a different failure is an outcome conflict.
- §8: "A conflicting … cause refuses mutation-free."
- Brief: exact replay must prove idempotence.

**Reproduction:**

```text
worker_exit_failure with a different failure -> same receipt
begin_delivery_non_success with a different cause -> same retirement
```

**Impact:** state is not mutated, but a conflict is reported as success. The second failure is discarded without filling its bounded diagnostic slot.

**Remedy:** compare the exact failure or cause identity; on mismatch, refuse with `OPERATION_OUTCOME_CONFLICT` without mutation.

**Closure test:** the two calls above refuse, with receipts and state unchanged.

### [P3-3] Source rules do not enumerate terminalizers and omit `run_worker_cleanup`

**Location:** `tests/contracts/test_contract_source_rules.py:74-103` (the worker-entry list has no `run_worker_cleanup`) and `161-183` (line 180 asserts only `specialized <= terminalizers`).

**Violated requirement:**
- Brief: "Syntax-aware checks enumerate … effect/exit entry points, terminalizers."
- Design §12.

**Evidence:** AST enumeration found nine terminalizing methods (`run_plan_step`, `complete`, `complete_contained`, `_commit_refresh_record`, `settle_contained_refresh`, `_dispose_refresh`, `settle_delivery_success`, `settle_delivery_non_success`, `_cancel_or_remove`). The rule pins only two of them.

**Impact:** a new generic path that terminalizes a handoff (the `ReviewCode-3 P2-1` class), or a cleanup entry that takes an identity, would pass the source rules cited as evidence.

**Remedy:** assert the exact terminalizer set, with a structural handoff-refusal guard for each generic terminalizer, and include every worker entry in the signature rule.

**Closure test:** adding a synthetic generic handoff terminalizer, or a cleanup parameter, fails the rule.

## 2. Invariant analysis

The attacks below failed against the build; they are what a future GO would rest on.

- **Specialized FIFO (`ReviewCode-3 P2-1`).** For every non-success cause, phase 1 leaves `delivered_through` at 0, retires the registration, invalidates and releases the successor once, and retains the active charge. Settlement before stop refuses. Phase 2 releases once and returns `RefetchRequired`; replay is read-only.

  ```text
  failure  PRE count/pub/cursors=(2, 3, (2, 0)) | PHASE1 (1, 3, (2, 0), 'retiring_refetch', 'retiring_handoff') succ=refused:refetch_required refused-before-stop | PHASE2 (0, 3, (2, 0), 'retired', 'refused') RefetchRequired | REPLAY (0, 3, (2, 0), 'retired') RefetchRequired
  ```

  The identical line was produced for `cancel`, `cleanup`, `expiry` and `receiver`. Fence, migration and graceful close gave `PHASE1 (1, 3, (2, 0), 'retiring_refetch', 'retiring_handoff', 'contained', True)`; migration was `migration-blocked:deadline_exceeded` until settlement and `migrating` afterwards. On refetch, `old-registration-refused:refetch_required`, and the new registration delivered `(1, 1)`. (The probe's residual count of 1 is its own abandoned refresh lease, which its caller still owns.)
- **Last-permit success race.**

  ```text
  migration  BEFORE-commit success-refused (1, 0, (1, 0), 'retiring_handoff', 'retiring_refetch', True) | AFTER-commit commit=(0, 1, (1, 1), 'succeeded') after-race=(0, 1, (1, 1), 'succeeded', True) late-non-success-refused
  ```

  The same holds for fence and receiver loss. No state showed count 0 with an unsettled head.
- **Participant lifecycle (`ReviewCode-3 P2-2`).**
  - `A2 preactivation admission: refused:activation_required`; `A3 preactivation join: refused:activation_required`.
  - Repro B: `B2 close_outcome: closed | membership: left`, `B3 … size: 1`, `B4 migration with only live ack: migrating`.
  - Tokens: copy, deepcopy and pickle raise `TypeError`; counterfeit and cross-coordinator tokens refuse `lease_invalid` with state unchanged.
  - Leave during an attempt: `required unchanged: True`; migration refuses until the leaving member acknowledges; after cutover `m1 left | m2 joined`; the later attempt is `{m2}` only.
  - The removed `register_participant()` refuses; duplicate `finalize_leave` refuses.
  - An active or retiring handoff holds a generation permit, so it does block finalization. The defect in P2-2 is confined to obligations that predicate does not see.
- **Initial 18 (Code IDs re-attacked).**
  - P2-1 / F1: worker and consumer entry signatures carry no callback, worker/task identity, stop flag or proof.
  - P2-2: pinned parameters, by inspection of 343-352 and 1130.
  - P2-3: strict step order; the separate ledger gap is P2-5.
  - P2-4: old admission after reopen refuses `admission_revoked`.
  - P2-5: cross-registry dequeue, settle and retire refuse with counts unchanged.
  - P2-6 / F9: issuing-task dequeue and effect are mutation-free, the genuine worker consumes once, and replay refuses `effect_ordinal_reused`; the cleanup gap is P2-4.
  - P2-7: five operation kinds only.
  - P2-8: close finalization before the barrier refuses with the runtime still `local_open`.
  - P2-9: same activation fence via membership.
  - State IDs were re-attacked only where touched: close released queued permits once; revocation, fence or receiver loss before commit published nothing. The remainder ran only as part of the passing suites.
- **Correction-1 13 / F1–F10.**
  - F1 signatures held.
  - F2 two-range success ended at `(2, 2)`, count 0, and later-before-earlier refused.
  - F3 wrong-fence withdrawal refused.
  - F4 frozen attempt held.
  - F7 generation 3 and same-generation requests both refused `generation_mismatch`.
  - F8 stale DRAINING proof refused with state unchanged; the exact pre-effect proof reopened once; replay refused.
  - F10 a closed target queue refused while its subscription stayed open.
  - F5 and F6 ran only as part of the passing suites.
- **Design-origin IDs touched by these probes.**
  - `Safety-2 P2-1` held.
  - `Safety-1 P2-1` held for delivery; the registration case is P2-7.
  - `Consistency-1 P2-2` (C1/C2) has gaps: P2-1 and P2-5.
  - `Consistency-1 P2-3` has a gap in the cleanup entry: P2-4.
  - `Consistency-2 P2-1` has gaps: P2-5(c) and P2-6.
  - `Consistency-1 P2-1` held.
- **Deferred, not reported:** production concurrency, locks, durability, crash recovery, real executor stop, physical activation, provenance, PostgreSQL and W3 names.

## 3. Risks and next action

**Residual risks below the finding bar:**
- `revoke_generation()` and barrier failures inside `settle_delivery_success` leave a handoff `CONTAINED` with no retirement until a caller presents a cause. This is recoverable today, but it is a state outside §8's named grammar.
- `commit_refresh`'s replay lookup scans every registration's ring in the registry rather than the target registration's.
- Hard fence leaves a continuation-owned non-delivery lease (after `RESULT_ACCEPTED`) `RUNNING` until its next barrier check.
- None of this is production evidence. The reference is deterministic and single-process.

**Next action:** the manager should consolidate P2-1 through P2-7 into one remediation plan and one consolidated source correction (implementation correction 1 of 2). None needs operator direction or an accepted-design change. The correction should add the closure tests specified above, and the originating Code axis should then re-run every reproduction in this report on the corrected tuple.
