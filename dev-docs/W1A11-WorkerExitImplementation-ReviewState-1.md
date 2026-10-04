# W1A11-WorkerExitImplementation — STATE-AXIS REVIEW

**Review object:** Candidate worker-exit internal contracts / deterministic reference implementation at the approved filesystem tuple `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`, SHA-256 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` (117 entries, not a Git commit); controlling DRAFT `dev-docs/W1A11-WorkerExitImplementation-DRAFT.md` at `e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`; status: candidate, STOP-WRITES in effect, implementation correction count zero, not accepted; 2026-10-04.
**Baseline:** Archived 20-file originals under `dev-docs/W1A11-WorkerExitImplementation-Baseline/` (`Baseline.sha256` `d95fab41…490a`, 20/20). All sources were read directly from the live filesystem at `/Volumes/projects/limbo/garns-wz/garns` (`cat -n`, `sed`, `diff -u` against the archive), never from Git HEAD. Accepted design `dev-docs/W1A11-WorkerExitRedesign.md` `167f6ce7…85fcc`; acceptance `884a0bfb…5d89`; accepted W2 base `0b8b77a0…7f44e` and overlay `01257e07…6bb26`.
**Date:** 2026-10-04
**Axis:** State — durable-state semantics and adversity: state machines and restart legality, write ordering, kill points between writes, races and lock scope, fail-closed direction, recovery states as a closed grammar (hunting new stuck states). Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — six P2 findings block (P2-1 … P2-6); three P3 findings are filed and do not block. No P0/P1. No new architectural root was found: every blocker is a transition-completeness defect inside the accepted single-lifetime-owner architecture and is a bounded source repair; none requires an accepted-design, ownership or compatibility change, so no operator STOP is triggered by this report. **I pre-commit to GO on a revision that resolves P2-1, P2-2, P2-3, P2-4, P2-5 and P2-6 as specified below**, with their closure tests, on a new frozen tuple.

---

## 0. Evidence base

### Tuple verification (START and END identical)

| Check | Expected | START | END |
|---|---|---:|---:|
| `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256` | `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544` | exact | exact |
| `shasum -a 256 -c …MANIFEST-1.sha256` | 117 OK | 117 OK | 117 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK | 31 / 20 / 741 | 31 / 20 / 741 |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 OK | all OK | all OK |
| WorkerExitRedesign-AcceptanceEvidence | 13 OK | 13 OK | 13 OK |
| DRAFT SHA-256 | `e8e2f73e…57ff2` | exact | exact |
| This prompt (`…ReviewState-Prompt-2.md`) | `dc57d5e6…236a2` | exact | exact |
| `.pyc` / `.pyo` / `__pycache__` under product root | 0 | 0 | 0 |
| `git status --porcelain` lines | 0 | — | 0 |

Historical live manifests were not checked against amended source; only the explicit Legacy rebased maps were used, as mandated. No file was written, no helper was spawned, no Git/GWZ/network/service operation was performed; `tools/check.py` was not run.

### Documents read completely

- Process authority: `/Users/owebeeone/.claude/skills/review-loop/SKILL.md` and `references/review-prompt-template.md`; `dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md` §§15–17 (lines 767–838); `dev-docs/W1A11-WorkerExitImplementation-ExecutionBrief.md`; `../AGENTS_GWZ.md`; product `AGENTS.md`; `docs/PRODUCT_LAYOUT.md`.
- Controlling design inputs: `W1A11-WorkerExitRedesign.md` (all 1,121 lines; §§2–11 cited by line below), `W1A11-WorkerExitRedesign-ACCEPTANCE.md`, `W2-AdmissionLifetimeRedesign.md` (overlay, all 853 lines), `W2-QueryPlanningDesign.md` (base), `W2-AdmissionLifetimeRedesign-ACCEPTANCE.md`, `W1-ACCEPTANCE.md`, `docs/adr/A16-admission-lifetime.md`, `docs/adr/README.md`.
- Historical stopped-source and design-gate reports named by Inputs: `W1A11-ContractAmendment-STOP.md`, `-ReviewState-3.md`, `-ReviewCode-3.md`, `-FreshCodeClosure-2.md`, `-OriginStateClosure-2.md`, `-RemPlan.md`, `-RemPlan-2.md`; `W1A11-WorkerExitRedesign-ReviewConsistency-3.md`, `-ReviewSafety-3.md`, `-OriginCodeClosure-3.md`, `-OriginCodeClosure-3-Erratum.md`, `-OriginStateClosure-3.md`.
- Candidate record and manager evidence: `W1A11-WorkerExitImplementation.md`, `-Verification-1.md`, `-VerificationLogs-1.md` (OK/PASS lines).
- Not read, by rule: any W1A11 Prompt-1/Prompt-2 file other than my own, any current-round Code review, closure or peer message.

### Source read completely (live bytes, line-numbered)

`src/garns/backends/contracts/lifetime_reference.py` (1–1780; state-critical ranges 178–235 construction/join, 290–355 acquire, 357–414 run_plan_step, 458–725 worker command ledger, 731–775 completion, 898–1116 refresh/neutral, 1118–1338 delivery, 1364–1486 close/migration/revocation, 1496–1780 private helpers), `buffer_reference.py` (1–502), `generation_reference.py` (1–561), `migration_reference.py` (1–127), `snapshot_reference.py` (1–181), `worker_authority.py` (1–143), `admission.py` (1–277), `values.py` (1–256), and the unchanged `authority.py`, `consumers.py`, `lifetime.py`, `protocols.py`, `__init__.py`, `operations.py`, `state.py`, `recovery.py`, `semantic.py`, `model.py`. All eight contract test files (`tests/contracts/*.py`, 2,845 lines) and `tests/support.py`. `diff -u` of all 15 changed baseline paths; `cmp` confirmed the five declared-identical files (`authority.py`, `consumers.py`, `lifetime.py`, `protocols.py`, `__init__.py`).

### Allowed gates executed (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B`)

| Interpreter | Command | Result |
|---|---|---|
| `/opt/homebrew/bin/python3.14` | `-m unittest discover -s tests/contracts -t .` | Ran 130, OK |
| `/opt/homebrew/bin/python3.14` | `-m unittest discover -s tests -t .` | Ran 233, OK |
| `/opt/homebrew/bin/python3.14` | `tools/check_product.py` | 5 PASS |
| `…/cpython-3.11…/bin/python3.11` | `-m unittest discover -s tests/contracts -t .` | Ran 130, OK |

Passing suites are corroboration only; none of the sequences below is exercised by them.

### Inline read-only attacks (stdin `python3.14 -B -`, real fixture transitions, no private state overwritten)

Probes A–J reproduced defects; K and O are positive-evidence attacks that held. Verbatim key output lines:

```text
A1 before (QUEUED, QUEUED, NOT_BEGUN, (frozenset({1}), frozenset()), None, False, 0, 1)
A1 refused worker_authority_invalid assigned worker is not current
A1 after  (CONTAINED, CONTAINED, NOT_BEGUN, (frozenset(), frozenset()), FAILURE, True, 0, 1)
A1 MUTATED ; A1 dequeue refused worker_authority_invalid command is not queued
A2 effect raised ContractRefusal effect lost its active reservation
A2 knowledge is not_begun (effect action actually executed)

B state after retirement begun: retiring_handoff count 1 cursors [2, 0]
B state after revoke_generation: contained count 1
B settle refused: lease_invalid delivery retirement is not quiescent   (x2)
B after hard close: state contained count 1 close: nonquiescent
B begin_migration refused: deadline_exceeded old generation is not quiescent
B final settle refused: lease_invalid … | count 1 registration retiring_refetch

C finalize_leave -> left | count still 1 ; attempt required participants: 0
C begin_migration refused: deadline_exceeded ; LEFT runtime barrier refused: migration_indeterminate
C start_close(runtime) raised AFTER mutation: lease_invalid membership is not joined | count now 0
C2 membership after reopen: left | runtime local: local_open
C2 LEFT-but-open runtime acquired a shared permit; count 1 ; later attempt required: 0

D cancel disposition: None | lease contained | command queue_removed | exit facts (None, None) | count 2 | registration active
D delivery_retirement refused … begin_delivery_non_success(None) refused … dispatch_worker again refused … complete_contained refused
D after graceful start_close(subscription): state retiring_handoff count 1

E close_outcome RAISED: lease_invalid membership retains obligations
E after close_outcome: {'runtime': 'local_closed', 'pool_a': 'local_closed', 'queue': 'local_closed'} admission retired membership leave_pending
E MUTATED BEFORE RAISE ; E2 repeated start_close(runtime) after LEFT raised: lease_invalid membership is not joined

F after hard fence: lease running owner is continuation? True command result_accepted count 1
F complete_contained refused: lease_owner_conflict ; run_plan_step refused: local_resource_fenced -> lease now contained
I accept refused: context_expired ; lease contained … command quiescent_success result still held? v
I complete_contained refused: lease_invalid contained command is not quiescent
J after queued C1 removal: lease cancelled_confirmed   (after LOWER had completed)

G dequeue raised ValueError trusted handoff command schedule must be finite and positive
G after: count 1 shared permits 1 buffer permits 0 active head set? True lease records 2
G after hard close: count 1 close -> closed ; begin_migration refused forever: deadline_exceeded count 1

H changed c2 RAISED refetch_required | lease running | candidate still current? True | count 2
H neutral c3 RAISED refetch_required 'neutral refresh lineage mismatch' | lease running | candidate still current? True

K1 after 20 neutral behind head: produced 21 delivered 0 sizes (1, 1, 9, 9) count 1 ; evicted/cross-registry/counterfeit -> RefreshRecordUnavailable
K1 after head settles: produced 21 delivered 21 spans 0 count 0
K2 barrier before commit: retiring_handoff count 1 delivered 0 ; late success refused ; settle -> RefetchRequired count 0 delivered 0 ; migration proceeds
K3 all attacks refused; state unchanged: True ; child-task accept refused: context_owner_mismatch
K4 stale candidate refused ; K5 cross-registry exit receipt as cause refused
O stale DRAINING proof in MIGRATING refused ; reopen before all acks refused ; pre-effect proof after publish refused
O rollback recovery: current 1 epoch 2 ; runtime hard close with retiring handoff: nonquiescent count 1 ; after settle: closed count 0 membership left
```

## 1. Findings

### [P2-1] `revoke_generation` overwrites `RETIRING_HANDOFF`, making the specialized second settlement permanently unreachable
**Location:** `src/garns/backends/contracts/lifetime_reference.py:1476-1486` (`revoke_generation` sets every non-terminal lease to `CONTAINED`); `:1329-1335` (`settle_delivery_non_success` requires `record.state is LeaseState.RETIRING_HANDOFF`); `:1693-1702` (`_revoke_worker_authorization` restores `RETIRING_HANDOFF` only inside its own cancel branch, which does not run for an already-contained command); `:1386-1390` and `:1449-1453` (`start_close(hard)` and `migration_queue_barrier` skip leases that already have a retirement, so they cannot repair it).
**Violated invariant:** Design §8 (lines 580–617): phase one "does not terminalize or release the active handoff"; only the second phase after exact stop may; "Close and migration … cannot cross their count/quiescence barrier until the specialized second phase commits" — the second phase must therefore remain reachable. Acceptance: "one authoritative owner and one exact release".
**Reproduction (probe B):** register; publish `(0,1]`,`(1,2]`; dequeue head; dispatch/dequeue worker; `worker_exit_failure`; `begin_delivery_non_success` → `RETIRING_HANDOFF`, count 1; `revoke_generation()` → lease `CONTAINED`; observe worker stop and delivery stop; `settle_delivery_non_success` → `LEASE_INVALID "delivery retirement is not quiescent"`, repeatedly. `settle_delivery_success`, `complete_contained`, generic `complete`, hard close of the subscription (`close_outcome` NONQUIESCENT), and `migration_queue_barrier` all leave it; `begin_migration` refuses with count 1.
**Impact:** A new permanently stuck state: the active handoff's shared permit can never be released, the registration stays `RETIRING_REFETCH`, the subscription can never report `CLOSED`, and deployment migration can never begin. No API path recovers. (Unrecoverable within the reference API; classified P2 because it is a contract/reference object, not a release.)
**Required correction (bounded):** Generic revocation/containment writers must not relabel a lease whose `delivery_retirement` is set (mirror the `start_close(hard)` skip), and/or key the second phase on `delivery_retirement`/`delivery_stop` rather than the outer state label. Also guard `_validate_barriers`' containment side effect (`:1524-1529`) the same way.
**Closure test:** retiring handoff (both failure- and receiver-loss-caused) → `revoke_generation` → worker stop + delivery stop → `settle_delivery_non_success` returns `RefetchRequired`; assert count 0, registration `RETIRED`, `delivered_through` unchanged, subscription `CLOSED`, `begin_migration` succeeds; replay settlement is read-only.

### [P2-2] `run_worker_cleanup` mutates on a wrong-task refusal and records stale effect knowledge during an in-flight effect
**Location:** `lifetime_reference.py:615-641`. No `command.state` precondition; the current-worker check (`:626-627`) is inside the `try`, so its `ContractRefusal` is caught at `:632` and converted by `:635-636` into a primary `FAILURE` containment with `command.effect_knowledge`; `finally` (`:640-641`) advances `next_cleanup_step` even for a refused call. `run_worker_effect` (`:521-525`) does not update `effect_knowledge` at reservation, so the value consumed here during `EFFECT_IN_FLIGHT` is the pre-reservation one.
**Violated invariant:** Design §7 row 1 — wrong current worker at dequeue/effect/exit "refusal before mutation; no effect, ordinal consumption, owner transfer or count change"; §4.1 edges (`QUEUED` → only `RUNNING_IDLE` or `QUEUE_REMOVED`; `BEGUN_UNCERTAIN` means reserved but not returned); §5.3 cleanup runs after the command body.
**Reproduction (probes A1, A2):** A1 — distinct worker provider; receiver (not worker) calls `run_worker_cleanup(auth, 1)` while the command is `QUEUED`: refusal `worker_authority_invalid` is raised, yet lease and command become `CONTAINED`, ordinals are revoked, a `FAILURE` exit receipt exists, and the real worker's `dequeue_worker` then refuses "command is not queued". A2 — cleanup provider raises; the effect action calls cleanup reentrantly during `EFFECT_IN_FLIGHT`: command contained with `effect_knowledge = NOT_BEGUN` although the effect ran; the returning effect then fails "lost its active reservation".
**Impact:** Any holder of the authorization running on the wrong task can kill a queued or running command (operation can never succeed); and the ledger can assert `NOT_BEGUN`/`RETURNED` for an effect that actually began — invented safety knowledge, the fail-closed direction violation on this axis.
**Required correction (bounded):** Before the `try`: require exact command state (`RUNNING_IDLE`, no active reservation), the exact current worker, and the exact next step; refuse mutation-free otherwise; only a raised cleanup action becomes a primary; do not advance the step on refusal; compute knowledge as `_cancel_or_remove` does (`BEGUN_UNCERTAIN` if a reservation is active).
**Closure test:** wrong-task cleanup in `QUEUED`, `RUNNING_IDLE`, `EFFECT_IN_FLIGHT` → refusal with identical (lease state, command state, ordinal sets, exit facts, `next_cleanup_step`, count); legitimate worker then dequeues/exits successfully; reentrant cleanup inside an effect refuses and the effect returns normally with `RETURNED`.

### [P2-3] Coordinator leave is not bound to the runtime's complete obligation set (buffer permits, local drain), so a non-idle runtime can become `LEFT`
**Location:** `generation_reference.py:130-144` (`request_leave` has no drain precondition; `finalize_leave`), `:516-517` (`_runtime_has_obligations` counts only shared `_permits`), `:525-528` (`_finish_pending_leaves`), `:264-275` and `:285-303` (buffer permits/exchanges carry `owner=_permit_owner` with no runtime attribution). Registry-mediated path: `lifetime_reference.py:1381-1382`, `1433-1438`. The membership token is a public property (`:236-238`) and the retained suite already drives `coordinator.request_leave` directly.
**Violated invariant:** Design §9 lines 683–688: `request_leave` "requires local runtime drain/fence and rejects new acquisition"; `finalize_leave` only when `LOCAL_CLOSED` and no "operation/generation permit, queued or active delivery, worker/containment record …"; A16 (`docs/adr/A16-admission-lifetime.md:80-84`) repeats it; a `LEFT` runtime is absent from every later attempt.
**Reproduction (probe C):** registration with one queued buffer (count 1): `coordinator.request_leave(registry.membership)` → `LEAVE_PENDING`; `finalize_leave` → `LEFT` with count still 1 and runtime `LOCAL_OPEN`. `begin_drain` freezes an empty required set; `begin_migration` refuses (count 1); the `LEFT` registry's `migration_queue_barrier` refuses, so nothing invalidates its buffer; `start_close(runtime)` releases it but itself raises `LEASE_INVALID "membership is not joined"` after mutating. C2: `request_leave` on an open runtime → auto-`LEFT` at attempt close → the open runtime keeps acquiring shared permits under `CURRENT` and is invisible to the next attempt.
**Impact:** Deployment-wide migration cannot complete while a `LEFT` runtime retains un-barriered permits; an `UNJOINED/JOINED/LEAVE_PENDING/LEFT` grammar that admits `LEFT` with retained charges. No progress is invented (count stays honest), but a stuck migration and a membership state the design excludes.
**Required correction (bounded, coordinator/registry seam only):** attribute buffer permits and exchanges to the issuing membership/runtime and count them in `_runtime_has_obligations`; make `request_leave` require the runtime's drain/fence evidence (or registry mediation) and refuse otherwise; `_finish_pending_leaves` must use the same complete check.
**Closure test:** queued buffer → direct request/finalize leave refuse with membership and count unchanged; after registry `start_close` + `close_outcome`, leave succeeds; `request_leave` on an open runtime refuses; a `LEFT` runtime never acquires; later attempt required set equals exactly the live members.

### [P2-4] Queue removal of a delivery's worker command issues no exit receipt and strands the handoff in generic `CONTAINED` outside the §8 grammar
**Location:** `lifetime_reference.py:1652-1663` (`_cancel_or_remove` `QUEUED` branch creates no `WorkerExitReceipt`; for `ITERATOR_HANDOFF` returns `None` at `:1659-1660` leaving `state = CONTAINED`); `:643-647` (`request_worker_cancel` returns that `None`); `:1248-1264` (`begin_delivery_non_success` accepts only a registry-issued exit receipt, lifecycle observation or closed failure).
**Violated invariant:** Design §4.1 line 166 defines `QUEUE_REMOVED(exit_receipt)`; §5.2 lines 329–332/348–352: removal creates `QUEUE_REMOVED` and "a delivery lease then uses §8's non-success retirement"; §8 lines 522–528 close the delivery grammar (`ACTIVE_HANDOFF`, `PUBLICATION_READY`, `RETIRING_HANDOFF`, `COMMITTED_SUCCESS`, `RETIRED_NON_SUCCESS`) — generic `CONTAINED` is not a member.
**Reproduction (probe D):** two queued ranges; dequeue head; `dispatch_worker`; `request_worker_cancel` → returns `None`; lease `CONTAINED`, command `QUEUE_REMOVED`, no exit receipt, registration still `ACTIVE` with an active head, count 2. `delivery_retirement`, `begin_delivery_non_success(lease, None)`, `dispatch_worker`, `complete_contained` all refuse; successor dequeue refuses (good). Only a close (`start_close(subscription)` → `RETIRING_HANDOFF`, count 1) or a migration barrier — or the fixture seam `setup_reference_worker_failure` — can begin retirement.
**Impact:** A new intermediate stuck state after an ordinary cancellation: the registration, successor permits and the active charge are frozen until an out-of-band close or migration; the receiver has no registry-issued cause to enter the mandated two-phase retirement. `close_outcome` stays `NONQUIESCENT` indefinitely.
**Required correction (bounded):** issue the `CANCEL` exit receipt on queue removal as the design states and, for `ITERATOR_HANDOFF`, enter phase one in the same mutation (or return the receipt as the exact cause).
**Closure test:** queued delivery command → `request_worker_cancel` → `RETIRING_HANDOFF` with successors invalidated exactly once and the active charge retained; delivery stop → `settle_delivery_non_success` → `RefetchRequired`, count 0, `delivered_through` unchanged; receiver-loss variant identical.

### [P2-5] Runtime close paths perform coordinator membership transitions after committing local state and without membership-state guards
**Location:** `lifetime_reference.py:1409-1439` (`close_outcome`): descendants transition to `LOCAL_CLOSED` (`:1424-1429`) and admissions to `RETIRED` (`:1431-1432`) before `finalize_leave` (`:1436-1438`), which raises when an attempt is open (`generation_reference.py:142-143`); `start_close` (`:1378-1382`) calls `request_leave` unconditionally, and `_membership_record` (`generation_reference.py:508-514`) refuses a `LEFT` membership.
**Violated invariant:** Overlay §4 / A16: "Owner transfer is validate-then-commit; a refusal preserves owner, state and charges"; design §9: a member closing during an attempt remains `LEAVE_PENDING` in the frozen set and must still acknowledge its barrier (local close must therefore be able to complete); close idempotency as exercised for subscriptions in the retained suite.
**Reproduction (probe E):** `begin_drain`; `start_close(runtime)` → `LEAVE_PENDING`; `close_outcome(runtime)` raises `LEASE_INVALID "membership retains obligations"` after every descendant became `LOCAL_CLOSED` and admissions `RETIRED`. After the attempt closes, `close_outcome` returns `CLOSED`. E2: a repeated `start_close(runtime)` (graceful or hard) after a completed close raises `LEASE_INVALID "membership is not joined"`.
**Impact:** The close linearization point reports failure for a close that committed; the refusal code mislabels a migration-topology condition as a lease error; repeated runtime close is not idempotent. Counts and permits are unaffected (diagnosability/recovery-grammar defect).
**Required correction (bounded):** evaluate the membership precondition before any mutation and return the local `CLOSED` outcome with membership left pending during an attempt (finalization then happens at attempt close), or refuse before mutating; make `start_close` skip `request_leave` when membership is already pending/left.
**Closure test:** `begin_drain` → `start_close(runtime)` → `close_outcome` returns `CLOSED`, membership `LEAVE_PENDING`, barrier acknowledges, attempt close → `LEFT`; repeated `start_close`/`close_outcome` are no-ops; any refusal leaves resource/admission states byte-identical.

### [P2-6] Refresh cursor divergence raises `REFETCH_REQUIRED` and leaves the known candidate current and the lease charged, without the §10 disposition
**Location:** `lifetime_reference.py:1013-1021` (`commit_neutral`) and `:1032-1037` (`create_candidate`) inside `_commit_refresh_record`; `buffer_reference.py:455-458` and `:159-174` raise on `previous != produced_through`; neither raise is routed through `_dispose_refresh` (`:1085-1116`), unlike queue-target/barrier failures (`:997-1001`) and retirement (`:1011-1012`). The cursor is checked only at candidate creation (`:923-924`), so two live candidates from one cursor are legal.
**Violated invariant:** Design §10 lines 783–800: a current candidate made unusable by "cursor divergence" either terminalizes `REFUSED` with one release and `RefetchRequired` (quiescent) or enters containment with `RefreshContainmentPending`; lines 811–812: no `RefetchRequired` is exposed for a known active candidate before its lease is terminal and released. This disposition was the accepted remedy of `Consistency-2 P2-1`.
**Reproduction (probe H):** three charged refresh leases prepared from `produced_through = 0` (neutral, changed, neutral); commit the first (neutral, count 3→2); `commit_refresh` of the changed and of the remaining neutral candidate each raise `ContractRefusal(REFETCH_REQUIRED)`; both leases remain `RUNNING`, their candidates remain current (`current_refresh_candidates` 2), count stays 2; replay raises again. Only the owner's generic `complete(..., REFUSED)` releases them.
**Impact:** The §10 closed grammar is not implemented for a legal interleaving; a known candidate yields a refusal exception while remaining current and charged; recovery depends on the caller knowing to use the generic completion (and, for a worker-backed refresh, cancel + `complete_contained`).
**Required correction (bounded):** check lineage before create/commit and route mismatch through `_dispose_refresh`, returning the typed disposition.
**Closure test:** two refreshes from one cursor → first commits; second returns `RefetchRequired`, lease `REFUSED`, count decremented once, candidate absent (`RefreshRecordUnavailable` on replay); worker-backed variant returns `RefreshContainmentPending` then `settle_contained_refresh` releases once.

### [P3-1] Fence/barrier containment of the outer lease is not atomic with the command-ledger transition
**Location:** `lifetime_reference.py:1383-1395` (`start_close(hard)`: when `authorization` is set it only revokes; `_revoke_worker_authorization` `:1693-1700` ignores `RESULT_ACCEPTED`, so an accepted-but-unpublished lease stays `RUNNING` under the continuation owner); `:1524-1529` (`_validate_barriers` sets the lease `CONTAINED` but leaves the command `QUIESCENT_SUCCESS` with its result value); `:771-774` (`complete_contained` then refuses "contained command is not quiescent").
**Violated invariant:** Design §4.1 edges `QUIESCENT_SUCCESS -> QUIESCENT_CONTAINED` (fence before accept) and §5.1/5.2 "closes the result and transfers to containment" as one mutation; §5.2 "after RESULT_ACCEPTED but before … publication … moves the already-quiescent outer lease to containment".
**Reproduction (probes F, I):** F — hard fence after accept: lease `RUNNING`, owner continuation; `complete_contained`/`complete` refuse; only a subsequent `run_plan_step` trips the barrier. I — context expiry at `accept_worker_result`: lease `CONTAINED`, command `QUIESCENT_SUCCESS`, result still held; `complete_contained` refuses until `request_worker_cancel` is also called.
**Impact:** Recoverable (receiver can take the second step; receiver loss also resolves), fail-closed holds; but an extra undocumented step and a misleading refusal message, and a retained private result after containment.
**Correction / test:** perform the command transition and result closure in the same mutation; test that `complete_contained` succeeds directly after each fence/barrier cause.

### [P3-2] `dequeue_buffer` validates the trusted handoff schedule after the permit exchange and FIFO dequeue commit
**Location:** `lifetime_reference.py:1141-1148` (exchange at 1141–1144, `commit_dequeue` 1144, schedule check 1146–1148 raises `ValueError` with no rollback) versus `_acquire` `:336-339` (same check, rolled back).
**Violated invariant:** validate-then-commit; `CLOSED` must not be reported while a permit attributable to the resource remains live (historical State P2-2).
**Reproduction (probe G):** provider returning `()` for `ITERATOR_HANDOFF`: `ValueError` after exchange → shared permits 1, buffer permits 0, active head set, no lease record; hard close then returns `CLOSED` with count 1; `begin_migration` refuses forever.
**Impact:** Reachable only through a misconfigured trusted setup provider (bounded), but the consequence is an orphaned permit, a headless active FIFO and a false `CLOSED`.
**Correction / test:** validate the schedule before the exchange (or roll back exchange and dequeue); test that an invalid handoff schedule leaves count, buffer permit, queue head and registration unchanged.

### [P3-3] Serial-1 queue removal after prior plan work is labelled `CANCELLED_CONFIRMED`
**Location:** `lifetime_reference.py:1661` (`outcome = CANCELLED_CONFIRMED if command.serial == 1`) with first dispatch permitted from `RUNNING` at `:471`.
**Violated invariant:** Design §4.1 lines 220–225: `CANCELLED_CONFIRMED` only "with no prior operation work or A7 identity"; §6 "only for an authoritatively not-started whole-operation cancellation".
**Reproduction (probe J):** `run_plan_step(LOWER)` → dispatch → cancel queued C1 → `CANCELLED_CONFIRMED`.
**Impact:** Terminal label asserts not-started for an operation that performed closed plan work (no effects, so no safety consequence; parity/diagnosability).
**Correction / test:** condition on `last_step_rank < 0 and not completed_steps`; test both labels.

## 2. Invariant analysis

**Attacks that held (evidence they held):**

- *Effect reservation before invoke, nonreentrancy, BaseException containment:* `test_baseexception_contains_before_escape_and_revokes_unused_effect`, `test_nested_reservation_refuses_without_consuming_second_ordinal`, `test_effect_failure_revokes_later_effect_and_retains_charge_through_stop`; source `run_worker_effect:507-546` reserves/removes the ordinal and sets `EFFECT_IN_FLIGHT` before the fixed action; nested call refuses at `:511`.
- *Exact executor quiescence; success escrow until stop and exact receiver acceptance:* `test_non_delivery_worker_publication_is_one_atomic_terminal_release`; probe K3 — forged authorization/exit receipt, wrong lease, premature success and generic completion of a worker-backed lease all refused with an identical state snapshot; child-task acceptance refused (`context_owner_mismatch`) with command still `QUIESCENT_SUCCESS`; original receiver then accepted.
- *C1/C2 tombstone isolation, one outer permit:* `test_two_commands_have_distinct_tombstones_under_one_outer_permit`, `test_first_and_later_queued_removal_have_distinct_terminal_outcomes` (later-serial removal → `REFUSED`, count 0 once).
- *Cleanup primacy/order:* `test_body_cleanup_and_cancel_cleanup_have_one_primary_receipt`, `test_cleanup_schedule_is_finite_and_ordered` (subject to P2-2's missing preconditions).
- *Task loss at every prepublication pause:* `test_task_loss_at_each_prepublication_phase_never_publishes`, `test_receiver_loss_contains_without_receiver_resumption`, `test_wrong_worker_and_lifecycle_identities_are_mutation_free` (counterfeit observation refused; exact replay idempotent).
- *Specialized delivery success is one commit; generic terminalizers refuse handoffs:* `test_delivery_success_is_one_publication_fifo_terminal_release_commit`, `test_delivery_commit_first_cannot_be_relabelled_by_late_barriers` (receiver loss, fence, revocation, migration after commit all leave `SUCCEEDED`, count 0); source rule `test_delivery_terminalization_has_only_specialized_success_and_retirement_calls` plus `test_shared_permit_release_is_centralized_in_terminalizer` (`_acquire`, `_terminalize` only); my trace of every `_terminalize` call site confirms no handoff reaches it except via the two specialized settlements.
- *Failed FIFO head: no invented delivery, successor invalidated once, active charge through stop:* `test_failed_fifo_head_retires_successors_and_holds_active_charge_until_stop` (cursors `(2,0)` retained), `test_precommit_expiry_fence_and_migration_all_retire_the_active_head`, `test_cancel_and_cleanup_failure_retire_two_range_registration`, `test_receiver_loss_after_publication_ready_routes_to_delivery_retirement`; probe K2 last-permit race: barrier before commit → `RETIRING_HANDOFF`, count 1, delivered 0, late success refused, settlement → count 0, migration proceeds. Double release excluded by `begin_handoff_retirement` (`buffer_reference.py:351-371`) returning `()` once `RETIRING_REFETCH`, and `retire_registration` skipping the `DEQUEUED` head.
- *Neutral lineage bounds and uniform absence:* probe K1 — 20 neutral commits behind a delayed changed head: `produced 21 / delivered 0`, exactly one span, ring 9 == C (Q=8), count 1; evicted candidate, cross-registry candidate and counterfeit all `RefreshRecordUnavailable`; head settlement folds to `delivered 21` with zero spans and count 0. Suite: `test_neutral_span_cannot_overtake_changed_head_and_folds_with_success`, `test_replay_window_is_exactly_c_and_evicted_handles_are_uniformly_unavailable`, `test_active_plus_q_changed_entries_overflow_retires_every_successor`, `test_changed_neutral_changed_preserves_two_exact_fifo_gaps`, `test_zero_queue_neutral_terminalizes_without_publication_or_buffer`, `test_known_candidate_wrong_owner_is_retryable_without_mutation`, `test_known_nonquiescent_candidate_retains_charge_until_exact_stop`, `test_refresh_publication_revalidates_every_barrier`. (P2-6 is the one §10 disposition not implemented.)
- *Phase/request-exact proof and closed product:* `test_drain_proof_is_stale_in_same_attempt_pre_effect_phase`, `test_effect_begun_has_no_pre_effect_reopen_edge`, `test_phase_product_and_request_identity_are_exact_at_every_stage`, `test_no_effect_reopen_requires_current_exact_proof_and_barriers`, `test_pre_effect_migrating_reopen_and_exact_successor_only`; probe O — reopen before all acknowledgements refused; stale `DRAINING` proof in `MIGRATING × MIGRATING_PRE_EFFECT` refused with product `(MIGRATING, MIGRATING_PRE_EFFECT, 2)`; proofs dead after `publish_generation`; `observe_request_released` refused in `INDETERMINATE`; full-rollback recovery → `CURRENT`, generation 1, epoch 2, attempt closed; old participant admission `admission_revoked`.
- *Activation-bracketed membership (original counterexamples):* `test_unjoined_runtime_has_no_admission_and_can_close_without_membership`, `test_membership_tokens_reject_copy_cross_stale_and_join_during_drain` (join during drain refused), `test_leave_pending_stays_in_frozen_attempt_then_disappears_from_later_attempt`, `test_leave_waits_for_operation_and_unresolved_close_obligations` (A7 unresolved identity independent of operation terminal state; `NONQUIESCENT` → `UNRESOLVED` → `CLOSED`/`LEFT`); probe O — runtime hard close with a retiring handoff stays `NONQUIESCENT` (count 1, `LEAVE_PENDING`) until settlement, then `CLOSED`/`LEFT`. Count zero never concealed resumable work in any normal path exercised.
- *Identity sealing:* all new identities are `_identity_type` empty slots classes, noncopyable/nonserializable (`test_private_handles_are_empty_exact_and_nontransferable`, `test_handles_are_empty_sealed…`); `object.__new__` counterfeits refused everywhere probed.

**Historical closure retrace (executable):**

| Root / IDs | Executable status on this tuple |
|---|---|
| Worker exit — `ReviewState-3 P2-1` | Original counterexample closed: effect 1 raises → contained before escape, effect 2 revoked, charge retained through stop (`test_effect_failure_revokes_later_effect…`, `test_baseexception_contains…`). Adjacent new defect in the same lifecycle: P2-2 (cleanup preconditions). |
| Failed FIFO — `ReviewCode-3 P2-1`, `ReviewState-3 P2-2`, `FreshCodeClosure-2 P2-1` (+`ReviewCode-2 P2-2`/`ReviewState-2 P2-1`) | Closed: refused/expired/fenced/cancelled/cleanup-failed head never advances `delivered_through`, successor cannot dequeue, queued permits released once, active charge retained through exact stop; two-range success retained (`test_two_buffer_ranges_are_delivered_fifo_with_one_active_head`); probe K2. Adjacent new defects: P2-1 (revocation strands phase two), P2-4 (queued-cancel route lacks a cause). |
| Participant lifecycle — `ReviewCode-3 P2-2` | Original two counterexamples closed (no preactivation admission; idle closed runtime leaves and is absent from the later attempt). Adjacent new defects: P2-3 (leave not bound to buffer permits/drain), P2-5 (close ordering). |
| Neutral refresh — `ReviewState-3 P2-3`, `Consistency-1 P2-4`, `Safety-1 P2-2`, `Consistency-2 P2-1/P2-2` | Closed on their sequences (zero-queue neutral, bounded coalesced spans, `R == C` ring, uniform unavailable, atomic terminal/release, nonquiescent containment). One §10 disposition missing: P2-6 (cursor divergence). |
| Phase proof — `OriginStateClosure-2 State-Closure-P2-1` (+`-1`), `Consistency-1 P2-1` | Closed: same-attempt stale `DRAINING` proof refused mutation-free; exact pre-effect proof reopens once; `EFFECT_BEGUN` has no edge; replay/cross/wrong-request refuse. |
| Initial 18 (`ReviewCode P2-1…9`, `ReviewState P2-1…8`, `State-Supp-P2-1`) and correction-1 13 (F1–F10) | Retained executable coverage confirmed by reading and running: F1/Code P2-1 (`test_guard_drives_effect_and_rejects_plan_escape_through_wrappers`, closed consumers), R2/P2-8 (pinned parameters; no `parameters` protocol argument), R3/State P2-4 incl. expanded revocation (`test_revocation_expiry_fence_and_graceful_old_generation`, `test_publication_is_committed_before_return…`), R4 (`test_no_effect_reopen_invalidates_old_admission_and_lease`), R5/State P2-3/F2 (`test_buffer_provenance_exchange_and_replay_refuse_without_count_change`), R6/F9 (worker-authority suite, dequeue current-worker checks), R7/State P2-7 (`test_static_and_live_operation_grammars_are_disjoint`), R8 (`test_open_close_finalization_refuses_without_mutation`, peer-local close), R9/F3/State P2-5 (`test_activation_negative_recovery_and_withdrawal_require_exact_proofs`), R10/State P2-1 (`test_generation_permits_are_exact_owned_and_replay_safe`), R11/State P2-2 (`test_close_invalidates_selected_buffers_once_and_not_peer`, `test_closed_waits_for_contained_handoff`), R12/State P2-6 (`test_migration_recovery_has_three_exact_proof_bearing_outcomes`), R13 (`test_rejected_transfer_is_atomic_and_old_owner_remains_usable`), F4 (`test_attempt_requires_every_exact_participant_barrier`, `test_migration_attempt_barrier_releases_multiple_queued_buffers_once`), F5 (sealed candidate tests), F6 (`test_parent_owned_derived_commands_share_one_permit_and_order`), F7 (exact successor), F8 (proof tests above), F10 (`test_snapshot_candidates_are_sealed_lease_bound_and_queue_fenced`). Five result vectors: `test_result_roles.py`. |

Those successful attacks do not cure the findings in §1.

## 3. Risks and next action

Below the finding bar (recorded, not filed):

- `begin_delivery_non_success` replays idempotently for any object once a retirement exists (`:1244-1245`), rather than refusing a conflicting/counterfeit cause; mutation-free, and the receipt is already obtainable via `delivery_retirement(lease)`.
- `create_candidate`'s overflow branch (`buffer_reference.py:175-181`) sets `RETIRING_REFETCH` without releasing permits or retiring the head; currently unreachable because `_commit_refresh_record` checks `changed_capacity_available` first — a latent hazard if that ordering changes.
- `observe_worker_stopped` writes `stop_receipt` before its final state check (`:702-710`); the raising branch is unreachable under current setup constraints.
- `first_lifetime_open` and `join_runtime` are two calls where the design describes one transaction; no adverse consequence found.
- `revoke_generation` is a coarse reference helper; its semantics as a production edge are not defined by the candidate record.
- Lease, observation, stop and proof records are retained forever in the reference registry (declared single-process limits); terminal lease records keep `result_value`/`refresh_snapshot` rows.
- Deferred by mandate and not reported: production async/thread/process execution, locks, durability/crash recovery, database provenance, activation fencing, credentials, W3 naming.

**Single next action:** keep STOP-WRITES; the lane owner merges this NO-GO with the Code axis and authorizes one consolidated bounded source correction (implementation correction 1 of at most 2) resolving P2-1 through P2-6 with the closure tests specified, freezes a new exact tuple, and returns it to the same reviewers for focused re-verdict with changed-range attacks. No accepted-design, ownership or compatibility change is required, so no operator STOP is implied by this report.
