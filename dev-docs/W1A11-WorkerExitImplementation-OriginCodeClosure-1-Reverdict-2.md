# W1A11-WorkerExitImplementation — OriginCodeClosure-1 / OriginCodeClosure-1-Reverdict FINAL RE-VERDICT (CODE-AXIS)

**Review object:** MANIFEST-3 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9` (141 entries), the corrected candidate after correction 2 of 2. This is an approved filesystem tuple, not a Git commit. Reviewed 2026-10-05.
**Prior reports:**
- `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1.md`, SHA-256 `d433a27ef452ad3ac3dbe294649c0c617fa8eae59ca99c2433fe5402c09f457e`
- `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1-Reverdict.md`, SHA-256 `134305d82cae745cd54abd16f27f2df0f3d806f2465813d076b61d2653f98ee5`

Both were re-verified at START and END.
**Reviewer:** Same agent as rounds 1 and 2. I am the originating Code closure reviewer, myself a disclosed replacement for the pre-round-1 origin agent. Model `claude-opus-5-5`, dispatched with model parameter `opus`. My context was continued, though compacted once earlier. Every counterexample below was re-executed in this session, not recalled.
**Axis:** Code. Originating executable closure of `ReviewCode-3 P2-1` (failed FIFO) and `ReviewCode-3 P2-2` (participant lifecycle), and of every finding I filed in rounds 1 and 2. Mandate: interface contracts against call sites, error paths, and DRAFT-versus-bytes conformance. Focused final re-verdict; independent, adversarial, read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO.**
- All eleven findings I filed earlier are CLOSED on MANIFEST-3: round 1 P2-1 to P2-7 and P3-1 to P3-3, and round 2 P2-8. Each original counterexample still reproduces on its own archive.
- Historical `ReviewCode-3 P2-2` is now fully CLOSED.
- Correction 2 introduced one new P2, **P2-9**. It is a regression caused by the IR23 cleanup-claim change, and it is bounded and not architectural. A success exit is now accepted while the last trusted cleanup action is still running. If that cleanup then fails, the failure is demoted to a diagnostic and the operation publishes success.
- On an iterator handoff, P2-9 settles a failed FIFO head as delivered and lets its successor proceed. That reopens the cleanup-failure cause of historical `ReviewCode-3 P2-1`, which is therefore PARTIALLY CLOSED.
- The implementation correction count is 2 of 2, so the lane stops for the operator's redesign-or-accept decision. I do not propose a third correction.

---

## Prior-finding closure table

"R1" is the Revision1 archive and "R2" the Revision2 archive. Each was run from inside the archive, so it resolves its own `src` and fixtures. "M3" is the live tree at MANIFEST-3. All probes are inline `-B` stdin scripts on Python 3.14.3.

| ID (report) | Disposition claimed (root) | Verified on MANIFEST-3 | Status |
|---|---|---|---|
| P2-1 (OCC-1): later-slot dispatch resurrects contained or retiring leases | IR8 | **N1** (M=2 EXECUTE, C1 accepted, receiver cancels, then C2 is dispatched):<br>• R1: `dispatch C2: ACCEPTED`.<br>• M3: `dispatch C2: refused:lease_invalid \| unchanged: True` over (state, owner, ledger, count, publications); `complete_contained -> refused count 0 publications 0`.<br>**N2** (two-slot delivery retired by migration barrier, close, fence, receiver loss or overflow):<br>• R1: strands the charge (`delivery worker has not stopped`).<br>• M3, every cause: `dispatch C2: refused (lease_invalid; context_owner_mismatch for receiver loss) \| unchanged: True \| settle: ACCEPTED count 0 delivered 0`. A late stop setup now replays (IR24), and migration proceeds after settlement. | **CLOSED** |
| P2-2 (OCC-1): leave finalized from generation permits alone | IR9 | **(a)** UNRESOLVED runtime across a no-effect reopen:<br>• R1: `left`, next attempt size 0.<br>• M3: `leave_pending`, `later attempt includes it: True \| size 1`.<br>**(b)** Public token on an open runtime holding a queued permit:<br>• R1: both ACCEPTED, membership `left`.<br>• M3: `request_leave: refused:local_resource_draining \| finalize_leave: refused:lease_invalid -> joined count 1`.<br>**(c)** Close during an attempt:<br>• R1: `raised lease_invalid` after closing.<br>• M3: `closed`, membership `leave_pending`, then `left` once the attempt closes. | **CLOSED** |
| P2-3 (OCC-1): formal coordinator seam lacks membership and proof members | IR10, extended by IR29 | • R1: the seam misses eight members and a membership-less stub conforms.<br>• M3: no member is missing, `recover_migration` now included; `begin_migration` returns `'MigrationRequestIdentity'`; the stub fails `isinstance`; the registry rejects it with "coordinator must satisfy the SharedGenerationCoordinator seam". | **CLOSED** |
| P2-4 (OCC-1): `run_worker_cleanup` validates inside its containment scope | IR7, rewritten by IR23 | **(a)** Wrong task calls cleanup at `running_idle`:<br>• R1: contained, `failure`, ordinals revoked, step 2.<br>• M3: `refused:worker_authority_invalid \| unchanged: True` over (state, knowledge, ordinals (1, 2), exit, owner, step 1). The genuine worker's next effect returns `('c', 1)`.<br>**(b)** Re-entrant cleanup inside effect 1:<br>• R1: `not_begun` recorded while the ordinal was in flight.<br>• M3: the nested call refuses and the effect returns 1, with knowledge `returned`.<br>A separate new root sits in the same entry; see P2-9. | **CLOSED** |
| P2-5 (OCC-1): publication bypasses the command ledger | IR1 | • R1: all four sequences below publish or terminalize.<br>• M3: (a) M=2 publish after C1 gives `refused:lease_invalid`, with (running, 1, 0) unchanged.<br>• M3: (b) default-provider publish while `running_idle` gives `refused:lease_invalid`, unchanged.<br>• M3: (c) neutral or changed commit while a distinct worker's command runs gives `RefreshCommitRefused \| unchanged: True ('running', 1, (0, 0), 1)`. | **CLOSED** |
| P2-6 (OCC-1): wrong-task refresh commit destroys the live refresh | IR3 | • R1: `RefetchRequired`, the lease ends `refused`, and the owner's retry gets `RefreshRecordUnavailable`.<br>• M3, changed and neutral candidates: `RefreshCommitRefused unchanged=True`. The owner's retry gives `BufferedDelivery` or `NeutralRefreshReceipt` exactly once. | **CLOSED** |
| P2-7 (OCC-1): registration not atomic with terminal success | IR2, adjacent to IR26 | • R1: returns `('publishing', 1, 1)`, then ends `refused` while the registration stays `active`.<br>• M3: returns `('succeeded', 0, 1)`. After receiver loss or cancel, `complete_contained` gives `refused:lease_invalid` and the final state is `('succeeded', 0, 'active')`.<br>• A superseded initial candidate gives `refused:refetch_required` with the lease unchanged (IR26). | **CLOSED** |
| P3-1 (OCC-1): first open not atomic with join | IR14 | • R1: `active` with 0 participants; withdrawal refused.<br>• M3: the handshake leaves `active_unused`; withdrawal ACCEPTED (back to `unactivated`); the first join gives `active`; withdrawal after the join refused. | **CLOSED** |
| P3-2 (OCC-1): replay accepts a different input | IR15 | • R1: both calls return the same record, with no conflict.<br>• M3: a different failure or cause gives `refused:operation_outcome_conflict`; exact replays return the same receipt or retirement. | **CLOSED** |
| P3-3 (OCC-1): source rules do not enumerate terminalizers | IR16 | • M3: the exact ten-terminalizer rule is present and matches my AST enumeration (`_commit_refresh_record, _contain_lease, _dispose_refresh, complete, complete_contained, register_subscription, run_plan_step, settle_contained_refresh, settle_delivery_non_success, settle_delivery_success`).<br>• The worker-entry rule includes `run_worker_cleanup`.<br>• R1: neither rule exists. | **CLOSED** |
| P2-8 (OCC-1-Reverdict): a runtime can join after its local close began | IR21 | • R2, graceful and hard: `open_lifetime after close began: ACCEPTED`; admission ACCEPTED; `close_outcome: raised local_resource_draining` with the runtime already `local_closed` and the membership `joined`; the next attempt requires the closed runtime (size 2); migration and reopen refuse.<br>• M3, graceful and hard: join `refused:local_resource_draining` with membership `None` and coordinator (participants, join serial, activation) unchanged; admission refused; `close_outcome: closed` through `close_unjoined`; a later join refuses; the next attempt has size 1; `begin_migration` and no-effect reopen proceed. | **CLOSED** |
| **Historical `ReviewCode-3 P2-1`** (failed FIFO), retaining `ReviewCode-2 P2-2` and `ReviewState-2 P2-1` | Design §8 (IR5, IR6, IR8, IR24) | Eight causes on M3: failure, cancel, cleanup, expiry, receiver loss, fence, close, migration. Every cause gives the same result:<br>• generic completions refuse;<br>• `PRE=(2, 3, (2, 0))`;<br>• phase 1 `(1, 3, (2, 0), 'retiring_refetch', 'retiring_handoff')`;<br>• the successor refuses and settlement before stop refuses;<br>• phase 2 `(0, 3, (2, 0), 'retired', 'refused') RefetchRequired`;<br>• replay is read-only and the late stop setup replays the same observation;<br>• migration is blocked until settlement, then `migrating`.<br>Refetch: the old registration refuses and the new one delivers `(1, 1)`. The last-permit race holds before and after the commit for migration, fence, receiver loss and generation.<br>**But P2-9 reopens the cleanup-failure cause.** A nested success exit inside the head's failing cleanup settles the head as delivered: cursors `(2, 1)` and the successor is `acquired` (R2: retired, `(2, 0)`). | **PARTIALLY CLOSED.** The original counterexample and every specified cause are closed; the cleanup-failure cause is reopened via P2-9. |
| **Historical `ReviewCode-3 P2-2`** (participant lifecycle) | Design §9 (IR9, IR10, IR14, IR21) | **Repro A:** no preactivation membership; admission and join refuse; a join in `ACTIVE_UNUSED` before the handshake refuses; the first join activates atomically.<br>**Repro B:** the closed member becomes `left`; the frozen set has size 1; migration proceeds on the live member's acknowledgement alone.<br>Also held: copy, deepcopy and pickle raise `TypeError`; counterfeit and cross-coordinator tokens refuse; a live operation blocks finalize; duplicates and `register_participant()` refuse; leave during an attempt keeps the set; cutover leaves `m1 left`, `m3 joined`. The join-after-close residual path (P2-8) is now closed. | **CLOSED** |
| F1, Code P2-1, `ReviewCode-2 P2-1`, `OriginCodeClosure-1 P2-1` (callback-free entries) | Retained | No worker or consumer entry has a callback, worker, task, stop or proof parameter (result: `[]`). | **HELD** |
| F9, Code P2-6, `OriginCodeClosure-1 P2-6` (trusted current worker) | Retained | Issuing-task dequeue and effect refuse with state unchanged; the genuine worker consumes once; replay refuses `effect_ordinal_reused`. The façade exposes only `context_owner` and `run_effect`. | **HELD** |
| F2, `ReviewCode-2 P2-2`, `ReviewState-2 P2-1` (FIFO) | Retained | Later-before-earlier refuses `refetch_required`. Two-range success ends at `(2, 2)` with count 0. | **HELD** |
| F3, `ReviewCode-2 P2-3` (same fence) | Retained | Wrong-fence withdrawal refuses and the state stays `active_unused`; same-fence withdrawal is ACCEPTED (`unactivated`). | **HELD** |
| F4, `ReviewState-2 P2-2` (frozen attempt) | Retained | The attempt set is unchanged by a leave; migration refuses `deadline_exceeded` before every member acknowledges. | **HELD** |
| F7, `ReviewState-2 P2-5` (exact successor) | Retained | Generation 3 and generation 1 both refuse `generation_mismatch`. | **HELD** |
| F8, `OriginStateClosure-1 State-Closure-P2-1` (phase proof) | Retained | A stale DRAINING proof refuses with state unchanged; the exact proof reopens once; replay refuses. | **HELD** |
| F10, `OriginCodeClosure-1 P2-3` (queue target) | Retained | A closed queue refuses `local_resource_fenced` while the subscription stays `local_open`. | **HELD** |
| Code P2-4 / P2-5 / P2-7 / P2-8 / P2-9 | Retained | • P2-4: old admission refuses `admission_revoked`.<br>• P2-5: cross-registry dequeue and a foreign lease refuse with counts unchanged.<br>• P2-7: five operation kinds.<br>• P2-8: close before the barrier refuses.<br>• P2-9: repro A. | **HELD** |

## Changed-range analysis

**Inventory.** Exactly 8 MANIFEST-2 paths changed relative to the Revision2 archive, matching DRAFT-3 and Verification-3.

| Path | Lines (R2 → M3) | diff lines |
|---|---|---:|
| `lifetime_reference.py` | 2,009 → 2,074 | 113 |
| `worker_authority.py` | 143 → 144 | 15 |
| `snapshot_reference.py` | 181 → 186 | 5 |
| `lifetime.py` | 344 → 346 | 2 |
| `test_worker_exit_contracts.py` | 2,682 → 3,200 | — |
| `test_contract_source_rules.py` | 340 → 413 | — |
| A16 | — | — |
| the implementation record | — | — |

`cmp` shows the other 15 allowlisted paths are byte-identical, including `buffer_reference.py`, `generation_reference.py` and five retained test modules. I read the complete source diffs.

**Correction-2 changes near my findings:**

| Root | Change | Finding it touches | Effect |
|---|---|---|---|
| IR21 | `_require_runtime_open` (325-337); `open_lifetime` (251-258); `_admit`; `start_close` sets `_runtime_close_begun` (1563) and relabels admissions only along legal edges; `close_outcome` (1586-1626) validates, then witnesses (1618), then mutates locally. | P2-8 | Closes it. A `close_outcome` refusal (a descendant re-opened after the barrier) leaves resources, admissions and membership unchanged. An open member still admits after cutover. |
| IR24 | The active serial is cleared at discard (2006); `setup_reference_delivery_stop` replays on a settled retirement. | P2-1, historical FIFO | Verified: replay returns the same observation and nothing raises. |
| IR25 | A late success from a non-worker refuses without mutation. | P3-2 neighbourhood | The worker's own late return still fills its diagnostic once. |
| IR26 | The initial candidate is tracked and discarded at terminalization. | P2-7 | Registration atomicity is unchanged; a superseded candidate refuses. |
| IR22 | `revoke` is removed from the façade. | — | Removes a containment route; none of my closures depended on it. |
| IR29 | `recover_migration` is added to the seam. | P2-3 | Strengthens it. |
| IR23 | `run_worker_cleanup` (697-748) claims the step before the action (733-735) and refuses re-entrant cleanup (707); `run_worker_effect` refuses reservation after cleanup begins (588). | P2-4 | P2-4's originals stay closed, but this change introduces P2-9. |

**Regression and new-root analysis:**
- **P2-9 is a NEW root and a regression of correction-1 behaviour.** IR23 made `next_cleanup_step` mean "steps claimed". `worker_exit_success` (line 664) still reads it as "every cleanup completed" and never consults `cleanup_in_progress`. R2 refused the same sequence with "trusted cleanup schedule is incomplete".
- P2-9 is bounded and **not architectural**: it is one precondition inside the existing sole lifetime owner, and needs no change to the accepted design, ownership or compatibility.
- No other correction-2 change regressed a closure of mine.
- **No NEW ARCHITECTURAL root cause.**

## 0. Evidence base

**Prompt.** `shasum -a 256 …-Reverdict-2-Prompt.md` gave `0a85d320…54c5` at START and END.

**Read:**
- RemPlan-2 `ab617c0f…678f`, all 317 lines.
- DRAFT-3 `62e2ec64…dede7`, complete.
- BuilderPrompt-3: its instructions and the IR21–IR30 build list.
- Verification-3 `6d039448…b6bd`, complete. I did not read VerificationLogs-3 `4b5677fc…a0a4`; I reproduced every gate myself.
- My two prior reports.

**Source:**
- Complete diffs of the four changed sources against R2.
- `lifetime_reference.py` lines 642-676 and 697-748.
- The outline of `CleanupClaimTests` in `test_worker_exit_contracts.py`. It checks success exit only between steps and after the last step returns; nothing calls it during a cleanup action.

**Not read:**
- `ReviewCode-3-Prompt.md` and `ReviewState-3-Prompt.md` (forbidden).
- Any `*-Reverdict-2.md` or round-3 report; none existed.
- Messages from other reviewers. I did not open other reviewers' reports.

**Tuple at START (23:06Z) and END (23:14Z), identical both times:**

| Check | Result |
|---|---|
| MANIFEST-3 SHA-256 | `9a9f8b2a…6af9` |
| MANIFEST-3 entries | 141/141 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK |
| Legacy 115 / 71 / 111 / 614 | all OK |
| AcceptanceEvidence | 13 OK |
| RemInputs / RemInputs-2 | 18 / 22 OK |
| Revision1 MANIFEST-1, verified inside the archive | 117 OK |
| Revision2 MANIFEST-2, verified inside the archive | 128 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 |

MANIFEST-1 and MANIFEST-2 were not checked against live source.

**Gates.** All runs used `PYTHONDONTWRITEBYTECODE=1`, the prescribed `PYTHONPATH` and `-B`, with no warning filter.

```text
[3.11.14] focused rc=0 Ran 187 tests OK | full rc=0 RW=0 Ran 290 tests OK | product rc=0 PASS=5
[3.12.12] focused rc=0 Ran 187 tests OK | full rc=0 RW=0 Ran 290 tests OK | product rc=0 PASS=5
[3.13.12] focused rc=0 Ran 187 tests OK | full rc=0 RW=112 Ran 290 tests OK | product rc=0 PASS=5
[3.14.3] focused rc=0 Ran 187 tests OK | full rc=0 RW=140 Ran 290 tests OK | product rc=0 PASS=5
```

Every gate passes on all four interpreters. None of them detects P2-9.

**Probes.** Each script was held in a shell variable and piped to stdin.
- Round-1 IDs ran on R1 and then M3.
- P2-8 and P2-9 ran on R2 and then M3.
- The historical and retained tables ran on M3.

Private fields were read only for observation and never assigned. Fixture-owned trusted providers (current task, clock, context) and fixed hostile trusted actions were driven the same way the builder's tests drive them. There were no file writes, Git/GWZ operations, network access, helpers, `tools/check.py`, `compileall` or `py_compile`.

## 1. Findings

### [P2-9] (new; regression introduced by correction 2) Success exit can commit while the last cleanup action is still running, so that cleanup's failure no longer prevents publication or FIFO settlement

**Classification:** new root inside IR23's changed range, regressing correction-1 behaviour. Bounded and **not architectural**. Under the 2-of-2 gate it stops the lane for an operator decision.

**Location:**
- `src/garns/backends/contracts/lifetime_reference.py:733-735`: `run_worker_cleanup` advances `next_cleanup_step` and sets `cleanup_begun` and `cleanup_in_progress` before the fixed action runs.
- `src/garns/backends/contracts/lifetime_reference.py:664`: `worker_exit_success` still decides "every trusted cleanup is complete" with `next_cleanup_step <= cleanup_steps`.
- `src/garns/backends/contracts/lifetime_reference.py:707`: `cleanup_in_progress` is consulted only here, by `run_worker_cleanup`. `worker_exit_success` never checks it.
- `src/garns/backends/contracts/lifetime_reference.py:738-746`: once a success receipt exists, a failure of the claimed step's action only fills a diagnostic slot.

**Violated invariant:**
- Accepted §5.1: the wrapper "performs every trusted cleanup before it requests success exit".
- Accepted §5.3: "Success exit is requested only after cleanup returns. Therefore cleanup cannot fail after a publishable success receipt exists." A first cleanup failure with no earlier error "is primary … closes/discards the result and transfers to containment".
- Accepted §4.2: a call made while the wrapper is already on this command's stack refuses.
- Accepted §8: a cleanup failure before publication retires the head, leaves delivered progress unchanged and keeps the successor from dequeuing. This is the historical `ReviewCode-3 P2-1` cause.
- RemPlan-2 IR23: success exit refuses until every step has run.

**Reproduction:** a trusted command with effect 1 and `cleanup_steps=1`. Its fixed cleanup action first calls `worker_exit_success(authorization, result)` and then raises.

(1) EXECUTE:
```text
R2: nested success exit inside cleanup step 1: refused:worker_authority_invalid | cleanup: cleanup raised
    after cleanup failure: command contained | exit kind failure | diagnostics 0 | lease contained | count 1
M3: nested success exit inside cleanup step 1: ACCEPTED receipt | cleanup: cleanup raised
    after cleanup failure: command success_pending | exit kind success | diagnostics 1 | lease running | count 1
    => accepted 'value-computed-before-cleanup' and published: succeeded | publications 1 | count 0
```

(2) Iterator handoff, with ranges `(0,1]` and `(1,2]` queued:
```text
R2: nested success inside failing head cleanup: refused:worker_authority_invalid | exit failure diagnostics 0 | handoff retiring_handoff | count 1
    => head retired: cursors (2, 0) | registration retiring_refetch
M3: nested success inside failing head cleanup: ACCEPTED | exit success diagnostics 1 | handoff running | count 2
    => head settled as delivered despite its cleanup failure: cursors (2, 1) | successor dequeued: acquired | publications 4
```

**Impact:**
- An operation whose trusted cleanup failed publishes `SUCCEEDED` and releases its generation charge.
- On an iterator handoff, a failed head is recorded as delivered and its successor proceeds. This is the false-delivered-progress class of `ReviewCode-3 P2-1`, now reachable again through the cleanup-failure cause.
- The suites pass because they check success exit only between steps.

**Required correction**, stated for whichever path the operator chooses; this is not a proposal for a third correction round:
- `worker_exit_success` must refuse without mutation while `cleanup_in_progress` is set.
- Equivalently, completion can be tracked separately from claiming: advance a completed-step counter only after an action returns, and require it to equal `cleanup_steps` with no action in progress.

**Closure test:**
- Both reproductions: the nested success exit refuses with the full vector unchanged.
- The cleanup failure then becomes the primary FAILURE (exit `failure`, 0 diagnostics), the lease is contained or the handoff retires, the count is retained and publications stay 0.
- Delivery cursors stay `(2, 0)` and the successor dequeue refuses.
- After stop, EXECUTE completes `REFUSED` with count 0, and the delivery settles through specialized non-success with count 0.

## 2. Invariant analysis

These attacks held on MANIFEST-3:

- **All eleven original counterexamples** (round 1 P2-1 to P2-7 and P3-1 to P3-3, round 2 P2-8) refuse with the full unchanged-state vector, or commit exactly once once their preconditions hold. Each still reproduces on its archive.
- **The specialized two-phase delivery settlement** holds for every cause as originally specified, including multi-command handoffs and overflow. The last-permit race holds on both sides of the commit.
- **Activation-bracketed membership** is complete, including join-after-close. Leave needs a witnessed CLOSED, and a `close_outcome` refusal mutates nothing.
- **The coordinator seam is complete and enforced.** The façade has no containment route.
- **Re-entrant cleanup for the same or the next step refuses**, effect reservation after cleanup begins refuses, and nested failure or cancel inside cleanup stays on the failure path. The defect is specific to success exit.
- **The retained initial-18 and F1–F10 obligations hold.**

## 3. Risks and next action

**Residual risks below the bar:**
- My round-2 residual is unchanged. Cleanup issued from inside an effect after an in-effect cancel is still accepted, but it records only a bounded diagnostic with correct `begun_uncertain` knowledge.
- The replay index is registry-wide rather than per registration.
- IR27 and IR28 are deferred to W3.
- A7 truth remains caller-supplied (RemPlan-2).
- All of this is deterministic single-process reference evidence only.

**Single next action:** the implementation correction count is 2 of 2 and a new P2 is open, so the lane stops. The operator decides between redesign and acceptance, with P2-9 and its reopening of historical `ReviewCode-3 P2-1`'s cleanup-failure cause as the decisive input.
