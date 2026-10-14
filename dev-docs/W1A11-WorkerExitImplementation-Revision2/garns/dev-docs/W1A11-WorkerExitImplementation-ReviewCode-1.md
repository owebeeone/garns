# W1A11-WorkerExitImplementation — CODE-AXIS REVIEW

**Review object:** Candidate worker-exit internal contracts/reference implementation at the approved filesystem tuple `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`, SHA-256 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` (117 entries; not a Git commit), compared with the archived 20-file baseline `dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256` (`d95fab41…f1a8c0c8`). Controlling DRAFT `dev-docs/W1A11-WorkerExitImplementation-DRAFT.md` at `e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`; implementation record `dev-docs/W1A11-WorkerExitImplementation.md` (`64626738…bc3783`). Status: candidate, builder writes stopped, not accepted. Reviewed 2026-10-04.
**Baseline:** Approved no-Git filesystem exception. Product root `/Volumes/projects/limbo/garns-wz/garns` (byte-exact relocation of the datascad path cited by historical documents). Sources were read directly from the filesystem tuple, never from Git HEAD; changed files were diffed with `diff -u`/`cmp` against `dev-docs/W1A11-WorkerExitImplementation-Baseline/`. Historical live manifests were checked only through the manager's rebased `Legacy-*` maps.
**Date:** 2026-10-04
**Axis:** Code — architecture, interfaces, call graphs, ownership/visibility, error and hidden-mutation paths, and whether the diff does what its DRAFT claims and nothing the accepted design forbids. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — no P0 or P1; eight P2 findings block (P2-1 … P2-8); seven P3 findings are filed and do not block. Every blocking finding is a bounded source repair inside the accepted design: each behaviour is already specified by `W1A11-WorkerExitRedesign.md` and was omitted or mis-wired, not redesigned. No accepted-design, ownership or compatibility change is required, so no STOP/operator direction is invoked and no architectural root is classified. I pre-commit to GO on a revision that resolves P2-1 through P2-8 as specified below.

---

## 0. Evidence base

### Tuple verification (START and END, identical results)

| Check | Result |
|---|---|
| `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256` | `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` |
| `shasum -a 256 -c` MANIFEST-1 | 117 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 OK |
| WorkerExitRedesign-AcceptanceEvidence | 13 OK |
| DRAFT SHA | `e8e2f73e…57f2` (unchanged) |
| Prompt SHA | `2d4d5281baa0d3cac1012f58452ef94be658a47777d297dee3ea8670848b4c07` (unchanged) |
| `.pyc`/`.pyo`/`__pycache__` under the tree | 0 before and after all runs |
| `git status --porcelain` | clean |

### Documents read in full

Workspace `../AGENTS_GWZ.md`; product `AGENTS.md`; `/Users/owebeeone/.claude/skills/review-loop/SKILL.md` and `references/review-prompt-template.md`; `GarnsV9-6-PostgresAsyncImplementationPlan.md` §§15–17 (lines 767–838); `docs/PRODUCT_LAYOUT.md`; the ExecutionBrief; the DRAFT; the implementation record; `W1A11-WorkerExitRedesign.md` (all 1,122 lines) and its ACCEPTANCE; `W2-AdmissionLifetimeRedesign.md` (all 854 lines); W2 composition ACCEPTANCE; W1-ACCEPTANCE; ADRs A6, A7, A11, A16, ADR README; `W1A11-ContractAmendment-{STOP,ReviewCode-3,ReviewState-3,FreshCodeClosure-2,OriginStateClosure-2,RemPlan,RemPlan-2}.md`; `W1A11-WorkerExitRedesign-{ReviewConsistency-3,ReviewSafety-3,OriginCodeClosure-3,OriginCodeClosure-3-Erratum,OriginStateClosure-3}.md`; `W1A11-WorkerExitImplementation-Verification-1.md`; `tools/check_product.py`. No current-round report, peer prompt or closure report was read.

### Source and tests read in full

`src/garns/backends/contracts/{admission,authority,buffer_reference,consumers,generation_reference,lifetime,lifetime_reference,migration_reference,protocols,snapshot_reference,values,worker_authority,__init__}.py`; `tests/contracts/{test_admission_contracts,test_contract_source_rules,test_contracts(fixture region),test_generation_contracts,test_lifetime_contracts,test_result_roles,test_worker_authority,test_worker_exit_contracts}.py`; `tests/support.py`; the complete baseline `test_worker_authority.py`.

Baseline comparison (`cmp`/`diff`): `authority.py`, `consumers.py`, `lifetime.py`, `protocols.py`, `__init__.py` IDENTICAL; `admission.py` +2 (two `LeaseState` members); `values.py` +18 (three refresh result types, three codes); `worker_authority.py` 223→143 (mutable `_WorkerRecord` table removed; sealed identity factory and stateless façade); `lifetime_reference.py` 796→1,780 (+1076/−92); `buffer_reference.py` 333→502; `generation_reference.py` 440→561; `migration_reference.py` 111→127; `snapshot_reference.py` +21; test diffs: `open_lifetime()` added to every fixture, `setup_reference_no_effect_proof` replaced by `observe_request_released`, handoff completions replaced by `settle_handoff`/`retire_handoff` helpers, old `complete(handoff, REFUSED)` paths removed; A16 +62/−23 candidate wording; README +3/−2.

### Gates executed (allowed commands, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`)

| Interpreter | `-B -m unittest discover -s tests/contracts -t .` | `-B -m unittest discover -s tests -t .` | `-B tools/check_product.py` |
|---|---:|---:|---:|
| /opt/homebrew/bin/python3.14 (3.14.3) | 130 OK | 233 OK (inherited SQLite `ResourceWarning`s visible, unfiltered) | 5 PASS |
| …/cpython-3.11…/python3.11 (3.11.14) | 130 OK | not run | 5 PASS |

A passing suite is treated as corroboration only; the verdict rests on the inline attacks below. `tools/check.py` was not run.

### Inline read-only attacks (`python3.14 -B -` on stdin, test fixtures from `tests/contracts`, no files written, no private state overwritten; private fields read only for observation)

Key observed outputs (full traces reproduced in the findings):

```text
P1a EXECUTE M=2, C1 accepted, C2 never dispatched: PUBLICATION -> OK; state succeeded publications 1 count 0
P1b EXECUTE M=1, zero dispatch: PUBLICATION -> OK; ledger_len 0 state succeeded count 0
P2  expiry between stop and accept: accept REFUSED context_expired; cmd quiescent_success lease contained;
    complete_contained REFUSED "contained command is not quiescent"; after receiver request_worker_cancel -> OK
P2b invalidation variant: identical
P3  hard fence on continuation-owned post-accept EXECUTE: lease running, owner continuation; close nonquiescent;
    complete_contained REFUSED lease_owner_conflict; complete REFUSED; other task cannot touch; receiving task
    PUBLICATION -> REFUSED local_resource_fenced -> contained -> complete_contained OK
P4  C2 dispatch: outer lease queued (design: remains RUNNING)
P5  different failure replay -> same receipt (idempotent); late success -> REFUSED, diagnostic count 0
P6  expiry at dequeue: lease contained, cmd queued, complete_contained REFUSED; receiver cancel -> cancelled_confirmed
P7  seal-minted counterfeits refused mutation-free   P8 wrong-task accept mutation-free   P9 C1 replay/conflict leaves C2 unchanged
R1  commit_refresh from WRONG TASK -> RefetchRequired; lease refused count 0 candidates 0; original authority -> RefreshRecordUnavailable
R2  two live refreshes previous=0: second commit -> ContractRefusal refetch_required; l2 running count 1; retry identical
R3  commit under DRAINING_OLD pre-barrier -> ContractRefusal generation_mismatch; lease contained, owner NOT containment,
    candidate still set, orphan CANDIDATE buffer record 1; retry -> RefetchRequired
R4  register_subscription: value returned, state publishing, publications 1, count 1; begin_migration REFUSED;
    separate complete(SUCCEEDED) releases
R5  coordinator.finalize_leave with one queued buffer -> left; LEFT runtime acquire -> OK count 2; drain required set 0;
    barrier REFUSED; begin_migration REFUSED deadline_exceeded count 2
R6  open_lifetime from ACTIVE_UNUSED -> REFUSED activation_required; ACTIVE with zero members reachable
R7  Protocol members lack: acknowledge_barrier admission_epoch barrier_allowed close_unjoined exchange_buffer_for_shared
    finalize_leave join_runtime membership_state no_effect_reopen_complete request_leave; registry typed to concrete class
D1  receiver cancels QUEUED delivery head: lease contained, cmd queue_removed, exit receipt None, retirement False,
    count 2; complete_contained REFUSED; no registry-issued cause exists; only setup_reference_worker_failure unlocks begin
D2  hard close on same shape -> retiring_handoff count 1 (manufactures its own cause)
D3  task loss at PUBLICATION_READY: contained, retirement False, count 2 until begin(observation)
D4  expiry at settle_delivery_success: contained, retirement False, count 2; shipped test passes the SUCCESS receipt as "cause"
D5  replay ring survives failed-head retirement (sizes (1,1,1,9) then (0,1,1,9); replay still OK)
D6  façade revoke() by authorization holder -> cancel containment; context_owner() returns the receiving task object
W1  issuing task run_effect after worker dequeue -> REFUSED, zero effects, state unchanged (holds)
W2  expiry before first effect -> REFUSED, contained NOT_BEGUN, zero effects, complete_contained OK (holds)
W3  cancel inside the fixed action -> BEGUN_UNCERTAIN, effect 2 refused, success refused (holds)
M1  close_outcome(runtime) during frozen attempt -> ContractRefusal "membership retains obligations" after resources already local_closed
G1  revoke_generation at PUBLICATION_READY -> contained, no retirement, count 2, delivery_retirement REFUSED
G2  receiver cancel at PUBLICATION_READY -> None, contained, count 2
S1  complete(SUCCEEDED) on live REFRESH -> succeeded, cursors (0,0), count 0 (inherited overlay edge)
```

## 1. Findings

### [P2-1] Non-delivery publication does not gate on the finite command schedule; required slots can be skipped

**Location:** `src/garns/backends/contracts/lifetime_reference.py:372-388` (`run_plan_step` PUBLICATION branch checks the ledger only when `record.kind is ITERATOR_HANDOFF`, lines 380-388); `register_subscription` 851-896 and `_commit_refresh_record` 980-1057 never consult `command_ledger`/`command_schedule`; `_acquire` 336-339 installs a non-empty schedule for every lease.
**Violated invariant:** Design §3 (lines 117-121) "exact finite positive command sequence and slot count M … Every slot is required"; §4.1 (212-218) "Public publication is legal only after serial M is RESULT_ACCEPTED, no command is active, the exact receiver remains live and every outer barrier is current. A non-delivery operation then uses the generic barrier in §6." ExecutionBrief: "The complete accepted design §§3–12 is mandatory."
**Reproduction:** (P1a) `build_fixture` with schedule `(c1,(1,)),(c2,(1,))`; acquire EXECUTE; LOWER; dispatch/dequeue/effect/success/stop/accept C1; `run_plan_step(PUBLICATION)` → `OK`; `lease_state=succeeded`, `publications=1`, `count=0`, ledger length 1 of schedule 2. (P1b) default M=1, never dispatch: LOWER then PUBLICATION → `succeeded`, ledger length 0. The retained suites (`test_lifetime_contracts.py:196-231`, `test_admission_contracts.py:230-246`) enshrine the zero-command path; `register()`/`publish()` helpers publish registrations and refreshes with no worker.
**Impact:** The schedule the registry itself requires to be "finite, positive and closed" is advisory for four of five operation kinds; an operation whose required C2 never ran terminalizes SUCCEEDED and counts a publication. `complete()` (746-750) refuses worker-backed leases, yet `run_plan_step(PUBLICATION)` publishes them regardless of ledger state. The DRAFT's "finite sequential command ledgers" claim holds only for iterator delivery.
**Classification:** bounded source repair (the ledger, schedule and gate exist; the gate is not applied uniformly).
**Required correction:** In `run_plan_step` PUBLICATION for every kind, in `register_subscription`, and before the changed/neutral commit in `_commit_refresh_record`, require `len(command_ledger) == len(command_schedule)`, last record `RESULT_ACCEPTED`, `active_command_serial is None`, receiver live. Adapt retained fixtures to drive the default command. Do not solve this by permitting an empty schedule — that would be a design change.
**Closure test:** M=2 EXECUTE: PUBLICATION after C1 refuses mutation-free (state, counts, publications unchanged); after C2 accepted publishes exactly once. M=1 zero-dispatch refuses for EXECUTE, CONSISTENT_SNAPSHOT, SNAPSHOT_REGISTRATION and REFRESH.

### [P2-2] Barrier-failure containment is lease-only: the active command is not moved to its contained state, so the containment owner cannot terminalize

**Location:** `lifetime_reference.py:1524-1529` (`_validate_barriers` catch block mutates only `record.state/owner`); `accept_worker_result` 712-725 (barrier at 720); `_validate_worker_barriers` 1604-1614 contains only `RUNNING_IDLE`/`EFFECT_IN_FLIGHT`; `dequeue_worker` 494-505; `complete_contained` 771-774 requires `QUIESCENT_CONTAINED`.
**Violated invariant:** Design §4.1 edges "SUCCESS_PENDING -> CONTAINED cancel/fence before stop", "QUIESCENT_SUCCESS -> QUIESCENT_CONTAINED fence before result accept", "QUEUED -> QUEUE_REMOVED authoritative queue removal"; §5.1 "expiry, invalidation or a hard fence closes the result and transfers to containment"; §5.2 cancellation sources include "an issuer-internal runtime fence/expiry/close event"; §5.2 "Only the registry containment owner may terminalize it after exact stop observation"; §7 row "Context expires or runtime hard-fences between success exit and accept".
**Reproduction:** (P2) dispatch/dequeue/effect/success/stop; `now=10.0`; `accept_worker_result` → REFUSED `context_expired`; `worker_command_state=quiescent_success`, `lease_state=contained`, `count=1`; `complete_contained` → REFUSED `lease_invalid "contained command is not quiescent"`; repeated accept refuses; only the expired receiver's `request_worker_cancel` moves the command to `quiescent_contained`, after which `complete_contained` succeeds. (P2b) `authority.invalidate(context)` identical. (P6) dispatch; `now=10.0`; `dequeue_worker` → REFUSED; lease `contained`, command `queued`; `complete_contained` REFUSED until the receiver cancels (→ `cancelled_confirmed`).
**Impact:** The designed contained command states are unreachable from the barrier that should produce them; the containment owner's sole terminal route refuses; terminalization depends on the already-expired receiving task issuing a cancel (or a task-loss observation / hard close). No false publication occurs.
**Classification:** bounded source repair.
**Required correction:** On `ContractRefusal` from the accept and dequeue barriers, apply the command transition (`SUCCESS_PENDING→CONTAINED` / `QUIESCENT_SUCCESS→QUIESCENT_CONTAINED` closing the result; `QUEUED→QUEUE_REMOVED` with the serial-sensitive outer disposition) — `_cancel_or_remove` already implements the mapping.
**Closure test:** expiry and invalidation between stop and accept → command `QUIESCENT_CONTAINED`, accept refuses, `complete_contained` succeeds from the containment owner without any receiver call, count 0; expiry at dequeue → serial 1 `CANCELLED_CONFIRMED`, serial 2 `REFUSED`, count 0.

### [P2-3] Hard fence does not transfer a post-acceptance, pre-publication non-delivery lease to containment

**Location:** `lifetime_reference.py:1383-1407` (`start_close(hard=True)`: when `record.authorization is not None` it only calls `self._workers.revoke`); `_revoke_worker_authorization` 1688-1702 acts only on `QUEUED/RUNNING_IDLE/EFFECT_IN_FLIGHT/SUCCESS_PENDING/QUIESCENT_SUCCESS`, so a lease whose last command is `RESULT_ACCEPTED` and whose owner is the `RuntimeContinuationOwner` is untouched. Contrast `revoke_generation` 1476-1486, which sets CONTAINED + containment owner first.
**Violated invariant:** Overlay §6 (lines 378-386) "Hard fence changes the selected resource to LOCAL_FENCED and its remaining leases to contained/revoked ownership … From its linearization point, no remaining selected lease may … publish"; design §5.2 "Hard fence and context invalidation use the same containment grammar … Only the registry containment owner may terminalize it".
**Reproduction:** (P3) EXECUTE; LOWER; C1 accepted (owner is continuation); `start_close(connection, hard=True)` → `lease_state=running`, owner still continuation; `close_outcome(connection)=nonquiescent`, count 1; `complete_contained` → REFUSED `lease_owner_conflict`; `complete(lease, task, REFUSED)` → REFUSED; from another task `run_plan_step`/`dispatch_worker` refuse before reaching the barrier; only the receiving task's own `run_plan_step(PUBLICATION)` trips `local_resource_fenced` and lazily contains, after which `complete_contained` succeeds. (P3b) the same fence with an active `QUIESCENT_SUCCESS` command is contained immediately.
**Impact:** After the fence, neither the containment owner nor the former owner can terminalize; the close stays NONQUIESCENT until the exact receiving task performs another barrier-checking call (or a task-loss observation / `revoke_generation` is used). The fence is not the linearization point the design requires.
**Classification:** bounded source repair.
**Required correction:** In the hard branch, after `revoke`, if the lease is non-terminal and not containment-owned (and not a retiring delivery), set `CONTAINED` and transfer to `containment_owner`, as the `else` branch and `revoke_generation` do.
**Closure test:** C1 accepted, continuation-owned; hard fence the connection → lease `CONTAINED`, containment-owned; `complete_contained` succeeds from any task; count 0; `close_outcome` CLOSED.

### [P2-4] `commit_refresh` disposes a known current candidate on a presentation-only (wrong-task) mismatch

**Location:** `lifetime_reference.py:997-1001` (`_commit_refresh_record` catches every `ContractRefusal` from `_validate_queue_target`/`_validate_barriers` and calls `_dispose_refresh`); `_validate_barriers` 1506-1509 raises `CONTEXT_OWNER_MISMATCH` through `RuntimeAuthority.validate` (`authority.py:62`) for a caller that is not the context's task; `_dispose_refresh` 1085-1116 terminalizes `REFUSED` and releases.
**Violated invariant:** Design §10 (lines 783-789) "A presentation-only mismatch that does not invalidate the recorded operation returns RefreshCommitRefused with candidate, owner, lease and charge unchanged, so only the original authority can retry"; (864-866) "A known current candidate presented under a wrong lease/authority refuses with its original owner and charge unchanged".
**Reproduction:** (R1) `make_lifetime_fixture`; `register`; `prepare_refresh(rev 1, rows=())`; set `fixture["task"][0]` to a fresh object; `commit_refresh(candidate)` → returns `RefetchRequired`; `lease_state=refused`, `count=0`, `current_refresh_candidates=0`; restoring the original task and retrying → `RefreshRecordUnavailable`. The shipped `test_known_candidate_wrong_owner_is_retryable_without_mutation` exercises only the wrong `owner` object through `publish_refresh_buffer`, never a wrong task through `commit_refresh`.
**Impact:** Any wrong-task presentation of a genuine candidate terminalizes a live charged refresh and strips the original authority of its operation; the recorded operation was never invalidated.
**Classification:** bounded source repair.
**Required correction:** Treat `CONTEXT_OWNER_MISMATCH` (and `LEASE_OWNER_CONFLICT`) as presentation-only in `_commit_refresh_record`: return `RefreshCommitRefused` with no mutation; keep the dispose route for expiry, invalidation, fence, generation, migration marker, retirement, overflow and cursor divergence.
**Closure test:** wrong-task `commit_refresh` → `RefreshCommitRefused`, lease RUNNING, count/candidate/cursors unchanged; original task then commits normally once.

### [P2-5] Cursor divergence at commit has no disposition: the stale refresh stays RUNNING and charged

**Location:** `lifetime_reference.py:1013-1021` (neutral) and `1032-1037` (changed) call `buffer_reference.commit_neutral` (456-457) / `create_candidate` (161-173) outside the dispose-guarded `try`; both raise `ContractRefusal(REFETCH_REQUIRED)` on `previous != produced_through`.
**Violated invariant:** Design §10 (789-800) "A current candidate made unusable by cursor divergence, registration retirement, overflow, close, fence or migration has an explicit operation disposition: if its worker is authoritatively quiescent, the same mutation removes the candidate from commit eligibility, records terminal REFUSED, releases its ancestry/generation charge once and returns RefetchRequired"; §10 contemplates several live charged refresh leases (`A <= L_refresh`).
**Reproduction:** (R2) two `prepare_refresh` leases at `previous=0`; `commit_refresh(c1)` → `NeutralRefreshReceipt`, produced 1; `commit_refresh(c2)` → raises `ContractRefusal(refetch_required, "neutral refresh lineage mismatch")`; `l2=running`, `count=1`, candidate retained; retry identical. Changed-row variant: `ContractRefusal(refetch_required, "refresh candidate provenance mismatch")`, `l2=running`, `count=2`.
**Impact:** A diverged refresh never terminalizes through its designed entry; its permit blocks drain/migration until the owner manually `complete`s; the typed result is replaced by an exception.
**Classification:** bounded source repair.
**Required correction:** Revalidate `snapshot.previous == produced_through` (and registration state) inside the guarded validation before `commit_neutral`/`create_candidate`, routing failure to `_dispose_refresh`.
**Closure test:** two refreshes from one cursor; the second commit returns `RefetchRequired`, lease `REFUSED`, count decremented once, later presentation `RefreshRecordUnavailable`; with a dispatched worker the same path yields `RefreshContainmentPending` until exact stop.

### [P2-6] `register_subscription` publishes without terminalizing or releasing — a separately callable releasing completion after publication

**Location:** `lifetime_reference.py:884-896` (sets `PUBLISHING`, `publication_committed`, `publications += 1`, consumes the candidate and returns rows/registration; no `_terminalize`); `complete` 755 still allows `PUBLISHING → SUCCEEDED`; the `register()` helper (`test_lifetime_contracts.py:101-102`) calls `complete(lease, owner, SUCCEEDED)` after publication. Byte-identical to the stopped baseline (baseline lines 495-501).
**Violated invariant:** Design §2 row 2 (line 64) "Neither operation kind has a separately callable releasing completion after publication"; §6 (448-452) "the generic barrier atomically records publication and terminal SUCCEEDED, releases ancestry charges and the shared permit exactly once, and only then makes the closed value available"; candidate A16 (this tuple) "Non-delivery publication atomically records visibility, terminal success and the one release"; DRAFT "Non-delivery publication atomically publishes, terminalizes and releases".
**Reproduction:** (R4) SNAPSHOT_REGISTRATION through FETCH/WATERMARK/candidate/REGISTRATION/ASSEMBLY; `register_subscription` returns `InitialSnapshotPublication` (value exposed); `lease_state=publishing`, `publications=1`, `count=1`; `begin_drain` + barrier; `begin_migration` → REFUSED `deadline_exceeded "old generation is not quiescent"`; `complete(REFUSED)` refuses; a separate `complete(SUCCEEDED)` releases (count 0). EXECUTE (`run_plan_step` PUBLICATION, 406-413) and REFRESH (`_commit_refresh_record` 1050-1056) were made atomic; this kind was not.
**Impact:** A published registration retains its generation charge indefinitely until a second call; migration and close are held by already-published work; the DRAFT/A16 atomicity claim is false for one of the five kinds — exactly the superseded "PUBLISHING then separately releasing completion" pattern.
**Classification:** bounded source repair.
**Required correction:** `_terminalize(record, LeaseState.SUCCEEDED)` inside `register_subscription` before returning; remove the trailing `complete` from the `register()` helper; drop `PUBLISHING → SUCCEEDED` from `complete`'s map if nothing else needs it.
**Closure test:** after `register_subscription`, state `SUCCEEDED` and count 0 in the same call; a later `complete(SUCCEEDED)` is idempotent and `complete(REFUSED)` conflicts; migration racing after the call sees a settled lease.

### [P2-7] Registry-detected delivery non-success neither begins §8 retirement nor issues a cause record; queued removal has no exit receipt

**Location:** `lifetime_reference.py:1653-1663` (`_cancel_or_remove` QUEUED branch: clears ordinals, sets `QUEUE_REMOVED`, no `WorkerExitReceipt`; for `ITERATOR_HANDOFF` returns `None` leaving `CONTAINED`); `settle_delivery_success` 1229 (`_validate_barriers` failure → `CONTAINED` only); `revoke_generation` 1476-1486 (no retirement for deliveries); `request_worker_cancel` 643-647; `begin_delivery_non_success` 1248-1264 accepts any `WorkerExitReceipt` of the lease, including a SUCCESS receipt. Only `start_close(hard)` 1396-1407, `migration_queue_barrier` 1448-1460 and `_retire_active_delivery` 1764-1780 manufacture an internal `ClosedWorkerFailure` and begin retirement.
**Violated invariant:** Design §4.1 `QUEUE_REMOVED(exit_receipt)`; §5.2 "Queued cancellation … creates QUEUE_REMOVED and applies the serial-sensitive outer disposition" and "a delivery lease invokes §8's first retirement phase and retains its active charge until the specialized quiescent settlement"; §8 "Every legal non-success before that commit uses two phases. First, begin_delivery_non_success validates a registry-owned cause record … Every input above is a registry-issued closed record, never a … caller-selected label".
**Reproduction:** (D1) two queued ranges; dequeue first; `dispatch_worker` (QUEUED); receiver `request_worker_cancel` → `None`; lease `contained`, command `queue_removed`, exit receipt `None`, `delivery_retirement` unset, `count=2` (successor still charged); successor dequeue refuses; `complete_contained` refuses; `settle_delivery_non_success` refuses; no registry-issued cause exists (`_failures` has none for this lease, `_active_exit` is `None`); only the fixture `setup_reference_worker_failure` unlocks `begin_delivery_non_success`. (G1) `revoke_generation` at `PUBLICATION_READY` → `contained`, no retirement, `count=2`, `delivery_retirement` refuses. (G2) receiver cancel at `PUBLICATION_READY` → `None`, `contained`, `count=2`. (D4) expiry at `settle_delivery_success` → `contained`, `count=2`; the shipped `test_precommit_expiry_fence_and_migration_all_retire_the_active_head` then passes the *success* exit receipt as the non-success cause. (D2) contrast: hard close on the D1 shape → `retiring_handoff`, `count=1`.
**Impact:** After a receiver cancel or an expiry/invalidation/generation revocation at the final barrier, the head is contained but un-retired, queued successors remain charged and neither invalidated nor dequeueable, and no production-shaped call can begin retirement; recovery depends on an unrelated hard close, migration barrier or overflow manufacturing a cause, or on a fixture. The §8 "exact non-success cause" is satisfiable by a success receipt (misleading interface).
**Classification:** bounded source repair (the retirement machinery exists; it is wired only into close/migration).
**Required correction:** Issue a CANCEL `WorkerExitReceipt` for `QUEUE_REMOVED`; have `_cancel_or_remove`, `revoke_generation` and the barrier-failure path of `settle_delivery_success` begin retirement for `ITERATOR_HANDOFF` leases (or return the registry-issued cause); refuse SUCCESS receipts as non-success causes.
**Closure test:** receiver cancel on a queued delivery head → `RETIRING_HANDOFF`, successor permits released exactly once, `delivery_retirement` available, stop + `settle_delivery_non_success` → `REFUSED`/`RefetchRequired`, count 0; same for expiry, invalidation and `revoke_generation` at `PUBLICATION_READY`; `begin_delivery_non_success(lease, success_receipt)` refuses mutation-free.

### [P2-8] Coordinator-side `finalize_leave` ignores queued delivery and `LOCAL_CLOSED`, and acquisition does not bind membership — a LEFT runtime keeps acquiring and blocks migration

**Location:** `generation_reference.py:137-144` (`finalize_leave` checks only `_current_attempt` and `_runtime_has_obligations`); `516-517` (`_runtime_has_obligations` scans `_permits` only); `_BufferPermitRecord` 41-46 carries no runtime identity; `acquire_shared` 223-236, `add_buffer` 263-274, `exchange_buffer_for_shared` 284-302 and `request_leave` 130-135 perform no membership check; `lifetime_reference.py:_acquire` 303-355 binds no membership/join serial (only `_admit` 278-279 checks `membership is None`).
**Violated invariant:** Design §9 (682-688) "finalize_leave removes the exact membership from future topology only when the runtime is LOCAL_CLOSED and has no operation/generation permit, queued or active delivery, worker/containment record, registration-close work or unresolved close obligation"; (662-663) "Admission records and leases bind the exact membership and join serial"; (682) "request_leave requires local runtime drain/fence and rejects new acquisition".
**Reproduction:** (R5) `register`; `publish` one range (`count=1`, no generation permits for the runtime); `coordinator.request_leave(registry.membership)` without any local drain → `leave_pending`; `coordinator.finalize_leave` → `left`, participants 0; `registry.acquire(EXECUTE)` → OK, `count=2`; `begin_drain` → required set size 0; the LEFT runtime's `migration_queue_barrier` → REFUSED `migration_indeterminate`; `begin_migration` → REFUSED `deadline_exceeded`, `count=2`. The registry-driven path (`close_outcome` 1420-1438) is safe because it reports NONQUIESCENT while buffers are queued; the design-named coordinator entry is not.
**Impact:** Through the coordinator entry the design names, a member with retained queued delivery leaves, then continues acquiring permits and buffers outside the frozen topology; a later attempt can never install its barrier nor reach zero, so migration is blocked until that runtime happens to drain itself.
**Classification:** bounded source repair (bookkeeping and gating inside the existing coordinator; no new owner).
**Required correction:** Record the owning runtime on buffer permits and count them in `_runtime_has_obligations`; require a JOINED membership (via the open record) in `acquire_shared`/`add_buffer`/`exchange_buffer_for_shared`; gate `request_leave`/`finalize_leave` on the registry's local state (accept only through the registry, or require a LOCAL_CLOSED attestation carried by the open record).
**Closure test:** direct `finalize_leave` with a queued buffer refuses without membership loss; `request_leave` without local drain refuses; after LEFT, `acquire`, `dequeue_buffer` and `add_buffer` refuse; a later attempt's required set excludes exactly the LEFT member and reaches zero.

### [P3-1] `close_outcome(runtime)` raises during a frozen attempt after already closing local resources

**Location:** `lifetime_reference.py:1424-1438` (resources → `LOCAL_CLOSED` and admissions → `RETIRED` precede `coordinator.finalize_leave`, which refuses while `_current_attempt is not None`, `generation_reference.py:141-142`).
**Violated invariant:** Design §9 "A member requested to leave during an attempt becomes LEAVE_PENDING, remains in that attempt's required set … After … the attempt closes, a quiescent LEAVE_PENDING member becomes LEFT"; §9 regression list "close during migration".
**Reproduction:** (M1) `begin_drain`; `start_close(runtime)` → `leave_pending`; `migration_queue_barrier`; `close_outcome(runtime)` → `ContractRefusal(lease_invalid, "membership retains obligations")`; runtime resource already `local_closed`; retry raises again; after `reopen_no_effect` the membership is `left` and `close_outcome` returns `CloseOutcome`.
**Impact:** A legal local close during an attempt returns an exception instead of `CLOSED`, after a partial mutation; the design's "close during migration" regression is not executed by any test.
**Remedy:** When the membership is `LEAVE_PENDING` and an attempt is current, return `CLOSED` without calling `finalize_leave` (`_finish_pending_leaves` already completes it), or validate before mutating. **Closure test:** close during an attempt → `CLOSED` with `LEAVE_PENDING`; after attempt close → `LEFT`.

### [P3-2] A later command's dispatch resets the outer lease state to `QUEUED`

**Location:** `lifetime_reference.py:491` (`record.state = LeaseState.QUEUED` for every `dispatch_worker`); `dequeue_worker` 498 requires outer `QUEUED`.
**Violated invariant:** Design §4.1 (203-207) "A later command's QUEUED is a private ledger state while the same outer lease remains RUNNING; it does not reset the lease".
**Reproduction:** (P4) C1 accepted → outer `running`; `dispatch_worker` C2 → outer `queued`, C2 `queued`.
**Impact:** `lease_state()` reports a state the design forbids for a running operation; outer-state consumers see a reset. No wrong terminal outcome was found (queued-removal remains serial-sensitive).
**Remedy:** keep outer `RUNNING` for `next_index > 0`; let `dequeue_worker` accept a ledger-QUEUED command under outer `RUNNING`. **Closure test:** after C2 dispatch, `lease_state` is `RUNNING` and `worker_command_state(C2)` is `QUEUED`.

### [P3-3] Exit replay/diagnostic grammar: a different failure replays as idempotent; late success is refused without the closed diagnostic

**Location:** `worker_exit_failure` 599-602 (returns the receipt for any failure of the command); `worker_exit_success` 571-574 and `_contain_command` 1624-1630 (raise `OPERATION_OUTCOME_CONFLICT`, record nothing).
**Violated invariant:** Design §6 "A different … failure … is an outcome conflict and changes nothing"; §4.1 "A late worker return after containment is recorded only as a closed diagnostic on that containment record"; brief "Exact replay must prove idempotence, not accept a generic label".
**Reproduction:** (P5) `worker_exit_failure(auth, failure2)` → same receipt as `failure1`; late `worker_exit_success` → REFUSED; diagnostic count stays 0.
**Impact:** diagnosability only; both paths are mutation-free. **Remedy:** compare the failure object as success does; record a bounded late-return diagnostic instead of raising. **Closure test:** different failure → conflict; late success → diagnostic count +1, state unchanged.

### [P3-4] Refresh commit under `DRAINING_OLD` before this participant's barrier raises mid-mutation and leaves inconsistent containment

**Location:** `lifetime_reference.py:1032-1049` (`create_candidate` registers a buffer record, then `add_buffer` refuses because the coordinator is not `CURRENT`; `except Exception` sets `CONTAINED` without transferring the owner and re-raises); `permit_live` (`generation_reference.py:253`) accepts the old binding under `DRAINING_OLD`, so `_validate_barriers` passes.
**Violated invariant:** Design §10 single-mutation disposition for a candidate made unusable by migration; overlay §8.2 step 4 "refuses/discards its candidate and releases its refresh lease without creating a buffer permit".
**Reproduction:** (R3) prepare a changed refresh; `begin_drain`; `commit_refresh` → `ContractRefusal(generation_mismatch, "buffer enqueue is fenced")`; lease `contained`, owner not containment, candidate still set, one orphan `CANDIDATE` buffer record, `count=1`; retry → `RefetchRequired`, count 0.
**Impact:** exception instead of a typed disposition; a lease that is `CONTAINED` but still caller-owned; orphan buffer record retained. Recoverable by retry. **Remedy:** check `coordinator.state is CURRENT` inside the guarded validation before `create_candidate`. **Closure test:** commit under `DRAINING_OLD` → `RefetchRequired`, lease `REFUSED`, count 0, no orphan record.

### [P3-5] `join_runtime` refuses the designed `ACTIVE_UNUSED` first-open edge; `ACTIVE` with zero members is reachable

**Location:** `generation_reference.py:107-108` (requires `ACTIVE`); `first_lifetime_open` 198-203 is a separate, join-free transition; every fixture calls both.
**Violated invariant:** Design §9 (657-661) "join_runtime … validates ACTIVE_UNUSED(epoch)/first-open or ACTIVE(epoch) … First open changes ACTIVE_UNUSED to ACTIVE in the same transaction."
**Reproduction:** (R6) `open_lifetime` from `active_unused` → REFUSED `activation_required`; `first_lifetime_open` alone → `active` with 0 members; `open_lifetime` then succeeds.
**Impact:** the designed atomic first-open-and-join is not modelled; the intermediate activated-but-memberless state exists. **Remedy:** let `join_runtime` perform `ACTIVE_UNUSED→ACTIVE` with the first join. **Closure test:** first open from `ACTIVE_UNUSED` activates and joins in one call; a second runtime joins under `ACTIVE`.

### [P3-6] The formal `SharedGenerationCoordinator` seam omits the join/leave lifecycle pair the originating finding required

**Location:** `src/garns/backends/contracts/lifetime.py:262-281` (unchanged from baseline; writable per the brief); `lifetime_reference.py:185` types the coordinator as the concrete `ReferenceGenerationCoordinator`.
**Violated invariant:** `W1A11-ContractAmendment-ReviewCode-3.md` P2-2 required correction "Add an exact participant join/leave contract to the formal protocol and reference coordinator"; design §13 assigns `lifetime.py` the "provisional internal seams".
**Reproduction:** (R7) Protocol members lack `join_runtime`, `request_leave`, `finalize_leave`, `close_unjoined`, `membership_state`, `acknowledge_barrier`, `barrier_allowed`, `exchange_buffer_for_shared`, `no_effect_reopen_complete`, `admission_epoch` — all called by the registry.
**Impact:** the lifecycle pair is absent from the seam a future authoritative coordinator must implement; a Protocol-conforming coordinator is unusable by the registry; the implementation record claims P2-2 coverage without the protocol half. **Remedy:** add the lifecycle (and the other used) members to the Protocol and type the registry against it, or record explicitly why the Protocol is not the seam. **Closure test:** static check that registry `self._coordinator.<x>` call sites ⊆ Protocol members.

### [P3-7] Mandatory enumeration/property tests and several §7 traces are absent, so the deviations above passed a green suite

**Location:** `tests/contracts/` (by inspection): no test enumerates the deployment-state × attempt-phase product rejecting every other pair/edge (`test_phase_product_and_request_identity_are_exact_at_every_stage` walks one path); no test enumerates `WorkerCommandState` edges; no test runs "context expires or runtime hard-fences between success exit and accept" to terminalization, "close during migration" through `close_outcome`, wrong-task `commit_refresh`, cursor divergence, receiver cancel of a queued delivery head, or the issuing task calling `run_effect` after the worker dequeued (the baseline `test_issuing_task_cannot_impersonate_assigned_worker` half; behaviour holds per W1).
**Violated invariant:** Design §11 "Its mandatory property test enumerates the entire product above and rejects every other edge/pair"; §12 "State-machine/property tests must enumerate every legal edge above and reject every other edge"; §7 rows; brief "Do not delete coverage merely because fixture entry points change".
**Impact:** P2-2, P2-3, P2-4, P2-5, P2-7, P3-1 and P3-2 are all on unexercised edges. **Remedy:** add the enumeration tests and the named traces. **Closure test:** the added tests fail on this tuple for the findings above and pass on the corrected tree.

## 2. Invariant analysis

Attacks that held (these are what the pre-commit rests on):

- **No raw Plan / arbitrary callback seam.** `ReferenceConsumerIssuer.consume`/`consume_command` run no caller code while holding the plan; `issue_consumer` takes only a label; protocol signatures carry no `Plan` (source rule + `test_protocols_have_no_raw_plan_executable_signature`); effects are `(authorization, ordinal)` resolved from the fixed `effect_provider` installed at construction. Worker entry signatures carry no callback/worker/task/stop/proof (`test_worker_entries_have_no_callback_or_caller_identity_override`, confirmed by reading 458-725).
- **Sole mutable owner.** `WorkerAuthorizationIssuer` holds three callables and no table (diff shows the baseline `_WorkerRecord` registry removed); `_participants`/cursor stores/proof issuance each have one owning module (source rule, confirmed); `release_shared` occurs only in `_acquire` (compensation) and `_terminalize`. No second worker-state owner was found in 1,780 lines.
- **Exact empty identities.** Minting through the (public) `_issuer_seal` yields exact-typed instances that every lookup refuses because lookups are identity-keyed in private dicts (P7); copy/deepcopy/pickle refuse; `__slots__ = ()`; repr exposes nothing. Wrong worker at dequeue, wrong task at accept (P8), counterfeit observation and cross-coordinator tokens refuse mutation-free.
- **Reserve-before-invoke, nonreentrancy, BaseException containment.** Effect 1 raising with effect 2 unused → `CONTAINED`, `BEGUN_UNCERTAIN`, both ordinals revoked, charge retained through stop; nested reservation refuses without consuming; cancellation landing inside the fixed action yields `BEGUN_UNCERTAIN`, blocks effect 2 and success (W3); expiry before the first effect gives `NOT_BEGUN`, zero effects, containment and `complete_contained` (W2); issuing task cannot run an effect (W1).
- **C1/C2 isolation and replay.** C1 effect/failure/authorization attacks against a running C2 refuse; exact C1 success/stop/accept replays are idempotent; C2 and the single outer permit are unchanged (P9). First-serial removal → `CANCELLED_CONFIRMED`, later-serial removal → `REFUSED` (shipped test, confirmed).
- **Primary receipt ordering.** Body failure commits before cleanup; cleanup-only failure is primary and discards the result; cancel/cleanup races keep one primary and a bounded diagnostic (shipped test, read).
- **Success escrow and stop.** Success exit publishes nothing; accept before stop refuses; accept after stop by the exact receiver returns the closed value; non-delivery publication then terminalizes and releases in one call (for EXECUTE — see P2-1/P2-6 for the gaps).
- **Specialized delivery commit.** `PUBLICATION_READY` holds no publication bit and no release; `complete`/`complete_contained` refuse `ITERATOR_HANDOFF`; `settle_delivery_success` publishes, pops/folds the head, advances `delivered_through`, terminalizes and releases in one call; replay returns the same settlement without a second release; counterfeit candidate refuses; receiver loss/fence/generation/migration after the commit cannot relabel it (shipped tests, confirmed by reading 1205-1236).
- **Two-phase retirement for worker-originated non-success.** Failed/cancelled/cleanup-failed head: `delivered_through` unchanged, successors invalidated and released once, active charge retained through worker stop + delivery stop, then `REFUSED`/`RefetchRequired`; successor can never dequeue (head stays active). Close and migration invoke the first phase and never double-release (`begin_handoff_retirement` returns `()` when already retiring).
- **Neutral lineage bounds.** `Q` from the authored bound (8), `C=R=9`; twelve neutrals behind one active head coalesce into one span and a 9-entry ring; the span folds with the head's success; changed-neutral-changed keeps two gaps; eviction makes candidate and receipt uniformly `RefreshRecordUnavailable`; a current candidate is counted only on a live charged lease (`A <= L_refresh`); overflow retires successors, retires the active head via §8 and disposes the triggering refresh; a nonquiescent known candidate returns `RefreshContainmentPending` until exact stop.
- **Phase proof.** `DRAINING_OLD` proof is stale after `begin_migration` on the same attempt (serial 1→2, new request identity); exact pre-effect proof reopens once; `EFFECT_BEGUN` (serial 3) removes the edge; wrong request, cross-coordinator and replay refuse with state/epoch unchanged.
- **Membership tokens.** Copy, cross-registry `request_leave`, join during drain and post-LEFT `request_leave` refuse; `LEAVE_PENDING` stays in the frozen required set and becomes `LEFT` at attempt close; pre-activation construction admits nothing and closes unjoined.
- **Result roles, pinned parameters, derived commands, A7 independence.** Five vectors lossless (`test_result_roles`); parameters pinned at acquisition and echoed by step products; child/total commands are ordinal-ordered under one parent permit with no independent kind; close knowledge keeps `NONQUIESCENT`/`UNRESOLVED`/`CLOSED` independent of transaction identities.

Attacks that failed are the findings in §1.

## 3. Risks and next action

Residual risks below the finding bar: the neutral replay ring is retained after a failed-head retirement (design permits retention; D5); the executor façade's `revoke()` is callable by any authorization holder (an unlisted but fail-closed cancel source) and `context_owner()` returns the receiving task object (D6); the inherited overlay edge `RUNNING → SUCCEEDED` via `complete()` labels a live REFRESH/SNAPSHOT_REGISTRATION "succeeded" with no progress (S1); `setup_reference_worker_stop` does not require cleanup completion for a `CONTAINED` command (fixture laxity, acknowledged by the DRAFT); `buffer_reference.invalidate()` is dead code with a divergent retirement semantic; task loss at `PUBLICATION_READY` needs a second explicit `begin_delivery_non_success(observation)` (the observation is at least a valid cause; D3). The 1,780-line `lifetime_reference.py` remains one cohesive owner; no second mutable owner was found, so the recorded size exception stands on its own terms.

Explicitly deferred outcomes (production async/thread/process execution, locks, durability, crash, provenance, PostgreSQL, activation, credentials, dependency/Git operations, W3 names) were not reported.

Single next action: apply one consolidated source correction resolving P2-1 … P2-8 as specified (all within the accepted design; no architecture, ownership or compatibility change), add the closure tests, re-freeze the tuple, and obtain focused re-verdicts plus originating executable closure on the corrected bytes. The five historical stopped roots remain OPEN until that closure; nothing in this report accepts source or alters the two-correction histories.
