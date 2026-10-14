# W1A11-WorkerExitImplementation — OriginCodeClosure-1 RE-VERDICT (CODE-AXIS)

**Review object:** MANIFEST-2 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` (128 entries), the corrected candidate after correction 1 of 2. This is an approved filesystem tuple, not a Git commit. Reviewed 2026-10-05.
**Prior report:** `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1.md`, SHA-256 `d433a27ef452ad3ac3dbe294649c0c617fa8eae59ca99c2433fe5402c09f457e` (re-verified at START and END).
**Reviewer:** Same agent as round 1: the round-1 originating Code closure reviewer, itself a disclosed replacement for the pre-round-1 origin agent. Model `claude-opus-5-5`, dispatched with model parameter `opus`. My context was continued, though the session was compacted once. Every counterexample below was re-executed in this session, not recalled.
**Axis:** Code. Originating executable closure of `ReviewCode-3 P2-1` (failed-FIFO accounting) and `ReviewCode-3 P2-2` (activation-bracketed participant lifecycle), plus my round-1 findings P2-1 to P2-7 and P3-1 to P3-3. Mandate: interface contracts against call sites, error paths, and DRAFT-versus-bytes conformance. Focused re-verdict; independent, adversarial, read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO.** All ten of my round-1 findings (seven P2, three P3) are CLOSED on the corrected tuple. I re-executed each original counterexample on the corrected tuple, and each still reproduces on the Revision1 archive. The original counterexamples of both historical roots remain closed. One new bounded P2 blocks: **P2-8**, a runtime can join after its local drain has begun. It reproduces the impact of `ReviewCode-3 P2-2` repro B through a path that IR9 did not cover. It is not architectural and needs no accepted-design change. I pre-commit to GO on a revision that resolves P2-8 as specified.

---

## Prior-finding closure table

"R1" means the Revision1 archive, run from inside `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns` so that it resolves its own `src` and fixtures. "Corrected" means the live tree at MANIFEST-2. All probes are inline `-B` stdin scripts on Python 3.14.3.

| ID | Disposition claimed (RemPlan root) | Verified on corrected tree | Status |
|---|---|---|---|
| P2-1 (later-slot dispatch) | IR8: validate the outer lease for every serial before mutating; later slots keep the outer lease `RUNNING` | **N1** (M=2 EXECUTE: C1 accepted, receiver cancels, then C2 is dispatched):<br>• R1: `dispatch C2: ACCEPTED`.<br>• Corrected: `dispatch C2: refused:lease_invalid \| unchanged: True` over (state, owner, ledger, count, publications); `complete_contained -> refused count 0 publications 0`.<br>**N2** (two-slot delivery, C1 accepted, then retired by migration barrier, close, fence, receiver loss or overflow):<br>• R1: strands the charge (`delivery worker has not stopped`).<br>• Corrected, each cause: `dispatch C2: refused (lease_invalid; context_owner_mismatch for receiver loss) \| unchanged: True \| settle: ACCEPTED count 0 \| delivered 0`. After the barrier, `begin_migration: ACCEPTED`.<br>A legal C2 dispatch keeps the outer lease `running` with C2 `queued`, and the stale C1 authorization refuses. Publication succeeds once, after both slots. | **CLOSED** |
| P2-2 (leave finalization predicate) | IR9: registry-witnessed close; permits bound to the member; validate before mutating | **(a)** UNRESOLVED runtime across a no-effect reopen:<br>• R1: `left`; the next attempt's required set is empty.<br>• Corrected: `leave_pending`; `later attempt includes it: True \| size 1`.<br>**(b)** Public token on an open runtime holding a queued permit:<br>• R1: both ACCEPTED, membership `left`.<br>• Corrected: `request_leave: refused:local_resource_draining \| finalize_leave: refused:lease_invalid -> joined count 1`.<br>**(c)** Close during a frozen attempt:<br>• R1: `raised lease_invalid` after closing.<br>• Corrected: `close_outcome during attempt: closed`, membership `leave_pending`, then `left` once the attempt closes.<br>Also on the corrected tree: a `LEFT` member's admission refuses `activation_required`, and an UNRESOLVED runtime goes CLOSED and then `left` once it resolves. | **CLOSED**. The root I filed is fixed. The adjacent new root is P2-8. |
| P2-3 (formal coordinator seam) | IR10: complete protocol; registry typed and checked against it | • R1: none of `join_runtime`, `request_leave`, `finalize_leave`, `close_unjoined`, `observe_request_released`, `reopen_no_effect`, `begin_migration_effect` is required, and a membership-less stub satisfies the seam.<br>• Corrected: all seven are required; `begin_migration` returns `'MigrationRequestIdentity'`; the stub fails `isinstance`; the registry constructor rejects it with "coordinator must satisfy the SharedGenerationCoordinator seam"; the reference coordinator conforms. | **CLOSED** |
| P2-4 (`run_worker_cleanup` validates inside its containment scope) | IR7: validate before the `try`; refusals consume no step; knowledge comes from reservation history | **(a)** Wrong task calls cleanup at `running_idle`:<br>• R1: the command is contained, `failure` is recorded, ordinals are revoked and the step goes to 2.<br>• Corrected: `refused:worker_authority_invalid \| unchanged: True` over (state, command state, knowledge, ordinals (1, 2), exit, owner, step 1). The genuine worker's next effect then returns `('c', 1)`.<br>**(b)** Re-entrant cleanup inside effect 1:<br>• R1: `not_begun` is recorded while ordinal 1 was in flight.<br>• Corrected: the nested call refuses and the effect returns 1, with knowledge `returned`, ordinal 1 completed and the step unconsumed. | **CLOSED** |
| P2-5 (publication bypasses the command ledger) | IR1: one publication precondition (M accepted, no active command, continuation owner, live receiver) | **R1:** all four sequences below publish or terminalize.<br>**Corrected:**<br>• (a) M=2 publish after C1: `refused:lease_invalid`, with (running, 1, 0) unchanged.<br>• (b) Default-provider publish while `running_idle`: `refused:lease_invalid`, unchanged.<br>• Zero-dispatch publish: `refused:lease_invalid`, count 1, publications 0.<br>• (c) Neutral or changed `commit_refresh` while a distinct worker's command is `running_idle`: `RefreshCommitRefused \| unchanged: True`. After the slot is accepted it commits once: neutral gives count 0, cursors (1, 1); changed gives count 1, cursors (1, 0). | **CLOSED** |
| P2-6 (wrong-task refresh commit destroys the live refresh) | IR3: presentation authority before barrier validation | • R1: `RefetchRequired`, the lease ends `refused`, and the owner's retry gets `RefreshRecordUnavailable`.<br>• Corrected, changed and neutral candidates: `RefreshCommitRefused unchanged=True ('running', 1, 1, (0, 0))`. Once publication-ready, the owner's retry gives `BufferedDelivery` or `NeutralRefreshReceipt` exactly once.<br>• The literal no-command sequence now refuses for both callers, because design §3 forbids a zero-dispatch commit. | **CLOSED** |
| P2-7 (registration not atomic with terminal success) | IR2: publication, registration, `SUCCEEDED` and release in one mutation | • R1: returns `('publishing', 1, 1)`; a later receiver loss or cancel then ends it `refused` while the registration stays `active` and delivers.<br>• Corrected: returns with `('succeeded', 0, 1)`. A later receiver loss or cancel leaves `complete_contained refused:lease_invalid`, the lease `succeeded` and the registration active.<br>• `complete(SUCCEEDED)` is accepted as a replay; `complete(REFUSED)` gives `operation_outcome_conflict`.<br>• A queue fence before the commit gives `local_resource_fenced`, with 0 registrations and 0 publications.<br>• Zero-dispatch registration refuses and creates no registration. | **CLOSED** |
| P3-1 (first open and join not atomic) | IR14 | • R1: `first_lifetime_open` reaches `active` with 0 participants, and withdrawal refuses.<br>• Corrected: the handshake leaves `active_unused`; withdrawal is ACCEPTED (back to `unactivated`); after re-activation, the first join gives `active`; withdrawal after the join refuses. | **CLOSED** |
| P3-2 (replay accepts a different input) | IR15 | • R1: both calls return the old record.<br>• Corrected: a different failure or a different cause gives `refused:operation_outcome_conflict`; exact replays return the same receipt or retirement. | **CLOSED** |
| P3-3 (source rules do not enumerate terminalizers) | IR16 | `test_terminalizers_are_exactly_enumerated_and_gated` pins the exact ten-method set, which matches my own AST enumeration:<br>`_commit_refresh_record, _contain_lease, _dispose_refresh, complete, complete_contained, register_subscription, run_plan_step, settle_contained_refresh, settle_delivery_non_success, settle_delivery_success`.<br>It gates the three generic success paths on the precondition. The worker-entry rule now includes `run_worker_cleanup` and an exact authorization-entry set. All rules pass in all four suites. | **CLOSED** |
| **Historical `ReviewCode-3 P2-1`** (failed FIFO), retaining `ReviewCode-2 P2-2` and `ReviewState-2 P2-1` | Design §8, strengthened by IR5, IR6 and IR8 | Re-run on the corrected tuple for eight causes: failure, cancel, cleanup, expiry, receiver loss, fence, close, migration. Every cause gives the same result:<br>• generic completions refuse `operation_outcome_conflict`;<br>• `PRE=(2, 3, (2, 0))`;<br>• phase 1 `(1, 3, (2, 0), 'retiring_refetch', 'retiring_handoff')`;<br>• the successor dequeue refuses and settlement before stop refuses;<br>• phase 2 `(0, 3, (2, 0), 'retired', 'refused') RefetchRequired`, with replay read-only;<br>• migration `blocked:deadline_exceeded` until settlement, then `migrating`.<br>Refetch: the old registration refuses and the new one delivers `(1, 1)`. Last-permit race: before the commit, migration, fence, receiver loss and now also `revoke_generation` all refuse success, keep count 1 and retire. After the commit the result is `(0, 1, (1, 1), 'succeeded')`, late barriers cannot relabel it and settlement replay is the same object. | **CLOSED** |
| **Historical `ReviewCode-3 P2-2`** (participant lifecycle) | Design §9 via IR9, IR10 and IR14 | **Repro A:** preactivation admission and join refuse `activation_required`; a join in `ACTIVE_UNUSED` before the handshake refuses; the first join activates atomically.<br>**Repro B:** the closed participant becomes `left`; the frozen set has size 1 and excludes it; migration proceeds on the live member's acknowledgement alone.<br>Also held: copy, deepcopy and pickle raise `TypeError`; counterfeit and cross-coordinator tokens refuse; a live operation blocks finalize; duplicates and the removed `register_participant()` refuse; leave during a frozen attempt keeps the set and is `left` after cutover.<br>**However, P2-8 reproduces repro B's impact through a join after the local drain has begun.** | **PARTIALLY CLOSED.** The original repros are closed; the residual path is open via P2-8. |
| Code P2-1, F1, `ReviewCode-2 P2-1`, `OriginCodeClosure-1 P2-1` (callback-free entries) | Retained | No worker or consumer entry has a callback, worker, task, stop or proof parameter (result: `[]`). | **HELD** |
| Code P2-6, F9, `OriginCodeClosure-1 P2-6` (trusted current worker) | Retained | Issuing-task dequeue and effect refuse with state unchanged; the genuine worker consumes once; replay refuses `effect_ordinal_reused`. The cleanup entry is now mutation-free too (P2-4). | **HELD** |
| F2, `ReviewCode-2 P2-2`, `ReviewState-2 P2-1` (FIFO) | Retained | Later-before-earlier refuses `refetch_required` with count 2. Two-range success ends at `(2, 2)` with count 0. | **HELD** |
| F3, `ReviewCode-2 P2-3` (same fence) | Retained | Wrong-fence withdrawal refuses and the state stays `active_unused`; same-fence withdrawal is ACCEPTED (`unactivated`). | **HELD** |
| F4, `ReviewState-2 P2-2` (frozen attempt) | Retained | Leave during an attempt keeps the required set; migration refuses `deadline_exceeded` until every member acknowledges. | **HELD** |
| F7, `ReviewState-2 P2-5` (exact successor) | Retained | Generation 3 and same-generation requests both refuse `generation_mismatch`. | **HELD** |
| F8, `OriginStateClosure-1 State-Closure-P2-1` (phase proof) | Retained | A stale DRAINING proof refuses with state unchanged; the exact pre-effect proof reopens once; replay refuses. | **HELD** |
| F10, `OriginCodeClosure-1 P2-3` (queue target) | Retained | A closed-queue candidate refuses `local_resource_fenced` while the subscription stays `local_open`. | **HELD** |
| Code P2-4 / P2-5 / P2-7 / P2-8 / P2-9 | Retained | • P2-4: old admission after reopen refuses `admission_revoked`.<br>• P2-5: cross-registry dequeue and a foreign lease refuse with counts unchanged.<br>• P2-7: five operation kinds only.<br>• P2-8: close before the barrier refuses with the runtime still `local_open`.<br>• P2-9: covered by repro A. | **HELD** |

## Changed-range analysis

**Inventory.** Exactly 13 MANIFEST-1 paths changed relative to the Revision1 archive, matching DRAFT-2 and Verification-2.

| Path | Lines (R1 → corrected) | diff lines |
|---|---|---:|
| `lifetime_reference.py` | 1,780 → 2,009 | 887 |
| `generation_reference.py` | 561 → 689 | 154 |
| `lifetime.py` | 299 → 344 | 59 |
| `buffer_reference.py` | 502 → 508 | 62 |
| `snapshot_reference.py` | 181 → 181 | 6 |
| six contract test modules | — | — |
| A16 | — | — |
| the implementation record | — | — |

`cmp` shows the other ten allowlisted paths are identical, including `admission.py`, `worker_authority.py`, `migration_reference.py`, `protocols.py`, `values.py`, `test_worker_authority.py` and the ADR README.

**My neighbourhoods against the RemPlan** (all line numbers in `lifetime_reference.py` unless stated):

| Finding | What the corrected code does | Matches RemPlan and accepted design |
|---|---|---|
| P2-1 | `dispatch_worker` (473-533) checks state, retirement, candidate, settlement, publication and owner before any write; later slots leave the outer lease `RUNNING`; `dequeue_worker` (535-550) accepts a ledger-`QUEUED` command under outer `RUNNING`. | Yes (§4.1, §4.2) |
| P2-2 | `witness_local_drain`/`witness_local_close`/`request_leave`/`finalize_leave`/`_leave_finishable`/`_finish_pending_leaves` in `generation_reference.py` (150-196, 637-655); member-bound permits there (282-385); `start_close`/`close_outcome` (1488-1551). | Yes for the leave predicate (§9) |
| P2-3 | `SharedGenerationCoordinator` in `lifetime.py` (266-326); `isinstance` check at registry construction (202-203). | Yes (§9, §11, §13) |
| P2-4 | `run_worker_cleanup` (660-701) validates everything before its `try`. | Yes (§5.3, §7 row 1) |
| P2-5 | `_publication_ready`/`_require_publication_ready` (1641-1661), required by `run_plan_step` (393-401), `register_subscription` (969), `_commit_refresh_record` (1147) and `prepare_delivery_publication` (1328). | Yes (§3, §4.1, §6) |
| P2-6 | `_presentation_current` (1638-1639), checked in `_validate_barriers` (1601-1604) and `_commit_refresh_record` (1107-1108, 1118-1120). | Yes (§10) |
| P2-7 | `register_subscription` (957-1006) terminalizes in the same call; `complete()` (803-837) records `SUCCEEDED` only as a replay. | Yes (§2 row 2, §6) |
| P3-1 | `join_runtime` (108-136) and `first_lifetime_open` (250-262) in `generation_reference.py`. | Yes (§9) |
| P3-2 | `worker_exit_failure` (648-651) and `begin_delivery_non_success` (1382-1387) compare the exact input. | Yes (§6, §8) |
| P3-3 | `test_contract_source_rules.py` lines 97-249. | Yes (§12) |

**DRAFT-2 interpretations I checked and accept**, each without mutation on refusal:
- The recorded delivery cause is the triggering registry record. Replay requires `cause is record.delivery_cause`.
- A usable refresh presented before every slot is accepted returns `RefreshCommitRefused`.
- `complete(SUCCEEDED)` is replay-only.
- `first_lifetime_open` is a handshake record only.

**Additions outside my dispositions:**
- The new protocol members `witness_local_drain` and `witness_local_close`. Only the holder of the exact `LifetimeOpenRecord` can present them. The names stay provisional for W3.
- The `lease_facts` and `worker_cleanup_step` observers.
- IR13 pruning and the replay index.
- The IR17 refusals.

None of them changes behaviour at my findings.

**New-root candidates:**
- **P2-8, bounded, not architectural.** `open_lifetime`/`join_runtime` never validate the local open resource. The defect pre-exists: R1 shows a silent `closed` with a `joined` ghost. The IR9 rewrite changed its symptom (`close_outcome` now raises after mutating) but did not add the §9 validation.
- Below the bar: cleanup is still accepted in the "contained before stop" state while a reservation from an in-effect cancel is active (see §3).

**No NEW ARCHITECTURAL root cause.** The implementation correction count is 1 of 2. P2-8 fits correction 2 without any accepted-design, ownership or compatibility change.

## 0. Evidence base

**Prompt.** `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-Reverdict-Prompt.md` gave `2c64f44e…0a12`, matching at START and END.

**Read in full:**
- RemPlan `a2d625e1…b2a1` (777 lines, all of it).
- DRAFT-2 `cf10c9f6…d30`.
- BuilderPrompt-2 `8f1bc939…176a`.
- Verification-2 `506d6bb1…2276`.
- VerificationLogs-2 `9cd61d67…924f`: headers and the result lines for all twelve runs.
- My filed round-1 report.

**Source read on the corrected tree:**
- `lifetime_reference.py` lines 1-2009 (complete) and `generation_reference.py` lines 1-689 (complete).
- `lifetime.py` lines 1-20 and 255-344.
- `test_contract_source_rules.py` lines 60-340.
- Fixture helpers: `test_admission_contracts.py` 36-100, `test_lifetime_contracts.py` 76-165, and `prepare_refresh` at `test_worker_exit_contracts.py` 51-71.
- `diff -u` of `buffer_reference.py` and `snapshot_reference.py` against R1.
- The archive's `tests/__init__.py` was confirmed identical to the live one. A run from inside the archive resolves the archive's fixtures and `src`, as printed.

**Not read:**
- `ReviewCode-2-Prompt.md` and `ReviewState-2-Prompt.md` (forbidden).
- Any `*-Reverdict.md`; none existed.
- Messages from other reviewers. I did not open the other round-1 reports either.

**Tuple at START (15:03Z) and END (15:16Z), identical both times:**

| Check | Result |
|---|---|
| MANIFEST-2 SHA-256 | `ee441c18…0720` |
| MANIFEST-2 entries | 128/128 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK |
| Legacy 115 / 71 / 111 / 614 | all OK |
| AcceptanceEvidence | 13 OK |
| RemInputs | 18 OK |
| Revision1 MANIFEST-1, verified inside the archive | 117 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 |

MANIFEST-1 was not checked against live source.

**Gates.** All runs used `PYTHONDONTWRITEBYTECODE=1`, the prescribed `PYTHONPATH` and `-B`, with no warning filter.

```text
[3.11.14] focused rc=0 Ran 173 tests OK | full rc=0 RW=0 Ran 276 tests OK | product rc=0 PASS=5
[3.12.12] focused rc=0 Ran 173 tests OK | full rc=0 RW=0 Ran 276 tests OK | product rc=0 PASS=5
[3.13.12] focused rc=0 Ran 173 tests OK | full rc=0 RW=116 Ran 276 tests OK | product rc=0 PASS=5
[3.14.3] focused rc=0 Ran 173 tests OK | full rc=0 RW=84 Ran 276 tests OK | product rc=0 PASS=5
```

**Probes.** Each script was held in a shell variable and piped to stdin. The same script ran in both trees: R1 first (from inside the archive), then the corrected tree. Key outputs are quoted in the closure table. Only one fixture adaptation was needed: two-slot schedules are scoped to the operation under test, because the corrected `register()`/`publish()` fixtures drive one default slot. Private fields were read only for observation and never assigned. Fixture-owned trusted providers (`task`, `now`, `context`) were driven the same way the builder's tests drive them.

**Procedural.** One zsh echo separator (`=====`) failed harmlessly. Apart from that, no file writes, Git/GWZ operations, network access, helpers, `tools/check.py`, `compileall` or `py_compile` were used.

## 1. Findings

### [P2-8] (new) A runtime can join after its local drain has begun; its close then leaves a `JOINED` ghost in later migration attempts

**Classification:** new root, found in the IR9 neighbourhood while re-checking P2-2. Bounded and not architectural. It pre-dates correction 1 but is not covered by IR9's disposition. It reproduces the impact of historical `ReviewCode-3 P2-2` repro B.

**Location:**
- `lifetime_reference.py:247-252`: `open_lifetime` has no local-state check.
- `generation_reference.py:108-136`: `join_runtime` validates activation, `CURRENT` and the absence of an attempt, but not the local open resource. The `LifetimeOpenRecord` created at lines 101-106 binds only a runtime identity.
- `lifetime_reference.py:1502-1512`: `start_close(runtime)` witnesses the drain and requests leave only if the runtime is already JOINED. For an unjoined runtime it records nothing.
- `lifetime_reference.py:1535-1550`: `close_outcome` sets the resources `LOCAL_CLOSED` and the admissions `RETIRED` before `witness_local_close`, which then refuses because the drain was never witnessed (`generation_reference.py:165-167`).
- `lifetime_reference.py:292-307`: `_admit` also ignores local state.

**Violated invariant:** accepted §9 says `join_runtime` "validates … runtime identity and local open resource". It also says a runtime closed before activation "performs only `UNJOINED -> LEFT` … later open/join on that registry refuses", and that a runtime which has left "can never become a permanent acknowledgement obligation". The RemPlan IR9 disposition requires that "`close_outcome` validates before mutating".

**Reproduction:** an active coordinator with one live participant. A second registry is constructed and its runtime resource added. Then `start_close(runtime)` runs while it is unjoined, followed by `open_lifetime()`, `close_outcome(runtime)`, `begin_drain`, the live member's barrier, and `begin_migration`.

```text
J1 runtime state before join: local_draining | membership None
J2 open_lifetime while draining: ACCEPTED | membership state: joined
J3 admission on draining runtime: ACCEPTED
J4 close_outcome: raised local_resource_draining | runtime local_closed | membership joined
J5 repeat close_outcome: raised local_resource_draining | membership joined
J6 later attempt requires the closed runtime: True | required size 2
J7 migration with only the live member acknowledging: refused:deadline_exceeded
J8 recovery by repeating start_close then close_outcome: closed | membership leave_pending
```

On R1 the same sequence gives `open_lifetime while draining: ACCEPTED joined`, then `close_outcome: closed | runtime local_closed | membership joined`, then `ghost in next attempt: True | migration: refused:deadline_exceeded`.

**Impact:**
- A locally closed runtime stays a JOINED participant in every later frozen attempt. Migration waits for an acknowledgement that a closed process cannot give.
- `close_outcome` reports a refusal after it has irreversibly closed local resources and retired admissions.
- An admission is minted on a draining runtime.
- Recovery needs a caller that already knows to repeat `start_close`. Even then, a member frozen into an open attempt stays `leave_pending` until that attempt closes.

**Required correction:**
- `open_lifetime` must refuse once the registry's runtime resource has left `LOCAL_OPEN`, or once a runtime close has begun. Equivalently, `start_close(runtime)` on an unjoined registry must close or mark its open record so that the coordinator refuses a later `join_runtime`.
- `close_outcome` must validate every coordinator precondition before its local mutation. If a membership exists, its drain must already be witnessed, or the drain must be witnessed first. It must never refuse after mutating.
- `_admit` must refuse when the runtime is not `LOCAL_OPEN`.

**Closure test:**
- `start_close(runtime)` while unjoined, then `open_lifetime()`: refuses with membership `None` and coordinator participants, join serial and activation unchanged.
- `close_outcome(runtime)` then returns CLOSED through `close_unjoined`, and a later join still refuses.
- A later attempt's required set excludes this runtime, and migration proceeds on the live members alone.
- Property check: any `close_outcome` refusal leaves resource states, admission states and membership unchanged.

## 2. Invariant analysis

These attacks held on the corrected tuple:

- **Every original counterexample is gone.** Each round-1 sequence for P2-1 to P2-7 and P3-1 to P3-3 now refuses with the full unchanged-state vector, or commits exactly once once its preconditions hold. Each still reproduces on R1 (closure table).
- **Two-phase delivery settlement is complete.** It survives every cause, including multi-command handoffs, overflow and `revoke_generation`. The `revoke_generation` case was a round-1 residual of mine and now enters retirement.
- **No released last permit with an unsettled head.** Commit-first is atomic and cannot be relabelled; barrier-first retires and keeps the charge until the exact stop.
- **The containment routine stays inside the grammar.** Terminal leases absorb, a retiring delivery keeps its label, and the lease and command move together. The hard fence after `RESULT_ACCEPTED` (my round-1 residual) now gives `(contained, None, 'containment')`, then `complete_contained` to count 0 and CLOSED.
- **The membership lifecycle holds** for every path the original reproductions exercise: activation bracketing, a witnessed CLOSED, a frozen attempt, cutover, tokens and duplicates.
- **The coordinator seam is complete and enforced**, both at construction time and by the source rule.
- **The retained initial-18 and F1–F10 obligations hold**, as tabled above.

## 3. Risks and next action

**Residual risks below the bar:**
- Re-entrant cleanup issued from inside an effect after an in-effect cancel is accepted as "contained before stop". It records only a bounded diagnostic, and its knowledge (`begun_uncertain`) and primary receipt are correct. Observed: `exit cancel knowledge begun_uncertain diagnostics 1 step 2`. The only deviation is that cleanup runs while the effect frame is still on the stack.
- The replay index is registry-wide rather than per registration. Its semantics are unchanged from round 1 and now cost constant work.
- All of this is deterministic single-process reference evidence only.

**Single next action:** include P2-8 in consolidated correction 2, with the closure test above, and then obtain my focused re-verdict on P2-8 and on the residual path of historical `ReviewCode-3 P2-2`.
