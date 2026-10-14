# W1A11-WorkerExitImplementation — OriginStateClosure-1 / OriginStateClosure-1-Reverdict FINAL RE-VERDICT (STATE-AXIS)

**Review object:** MANIFEST-3 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9` (141 entries). This is the corrected candidate after correction 2 of 2: an approved filesystem tuple at `/Volumes/projects/limbo/garns-wz/garns`, not a Git commit. Date: 2026-10-05 local. Tuple checks ran on the UTC clock from START 23:06 to END 23:29 on 2026-10-04.

**Prior reports:**
- `dev-docs/W1A11-WorkerExitImplementation-OriginStateClosure-1.md`, SHA-256 `d1add3b62da7c0e1564bf227878dedb62058292e23f00fd3eece65bbed1888c2` (round 1, MANIFEST-1).
- `dev-docs/W1A11-WorkerExitImplementation-OriginStateClosure-1-Reverdict.md`, SHA-256 `43428228184450d8f93c08eb631951d07653be1a3528918a167d9fff60e0a0e4` (round 2, MANIFEST-2).

**Reviewer:** Same agent as rounds 1 and 2: a Claude subagent, model `claude-opus-5-5`, dispatched with parameter "opus". This is the replacement originating State closure reviewer disclosed in round 1. My context is intact.
- The harness compacted my conversation between rounds, and once during this round.
- My earlier reports, and every pre-compaction command result cited here, stayed available to me verbatim.
- The historical-root retrace, the P2-9 variants, the suites and END verification all ran after that compaction.

**Axis:** State: durable-state semantics and adversity. This is the originating State executable closure of my 15 findings and of the historical stopped State roots. It is a focused final re-verdict: independent, adversarial and read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new P2 blocks; every P0–P2 filed before this round is closed.
- **Round-1 and round-2 findings:**
  - All eight P2s (P2-1 to P2-8) are **CLOSED** on MANIFEST-3.
  - P3-1, P3-2, P3-3, P3-4 and P3-6 are **CLOSED**.
  - P3-5 and P3-7 stay **OPEN**. The operator deferred them to W3 (IR27, IR28). They do not block.
- **Historical roots:** the original counterexamples of all four historical stopped State roots stay closed, and the retained obligations hold. However, the worker-exit root is open again through the new P2-9.
- **New P2-9:** correction 2 counts the final cleanup step as complete before its action returns.
  - A re-entrant success exit from inside that action therefore commits success. A cleanup failure after it is recorded only as a diagnostic, and the result is then accepted and published.
  - This is a regression of correction-1 behaviour: Revision2 refused that re-entrant success.
  - It is bounded and **not architectural**.
- **No NEW ARCHITECTURAL root cause** was found.
- **Gate:** the implementation correction count is 2 of 2. This verdict stops the lane, and the operator decides between redesign and acceptance. I propose no third correction.

---

## Prior-finding closure table

How to read this table:
- "R1" and "R2" mean the same inline attack, run from identical script text inside the Revision1 or Revision2 archive.
- A "vector" is the lease facts, publications, coordinator count and command facts.
- A count transition such as "count 2→1" is the coordinator's permit count.

| ID (report) | Disposition claimed (root) | Verified on MANIFEST-3 | Status |
|---|---|---|---|
| P2-1 (OriginStateClosure-1) — publication bypasses the worker-exit ledger | IR1: one publication precondition on every non-delivery terminal success; zero-dispatch publication refuses; continuation-owner path for registration and refresh | **(a)** PUBLICATION while the command is RUNNING_IDLE (default provider): `lease_invalid`, vector unchanged (RUNNING, no completion, `running_idle`, count 1, publications 0). **(b)** PUBLICATION from inside effect 1 refuses; `begin_migration` then gets `deadline_exceeded` at count 1 in DRAINING_OLD. **(c)** Distinct worker W running, neutral `commit_refresh`, and **(d)** changed publish while running: both `RefreshCommitRefused`, facts unchanged, migration refused. **(e)** Registration while running: `lease_invalid`, +0 registrations. After acceptance, one call publishes, terminalizes SUCCEEDED and releases (count 0, publications 1, +1 registration). Then `complete(SUCCEEDED)` replays, `complete(REFUSED)` conflicts, and a late cancel is a no-op. **Zero-dispatch** publish: `lease_invalid`. **Stage matrix:** SUCCESS_PENDING and QUIESCENT_SUCCESS get `lease_owner_conflict`, after C1 of M=2 `lease_invalid`, each with the vector unchanged. R1 still publishes in every case | **CLOSED** |
| P2-2 (OriginStateClosure-1) — containment writers revive terminal leases | IR6: terminal leases absorbing; retiring deliveries untouched | **Literal (b):** cancelling the queued command returns a receipt; the lease is CANCELLED_CONFIRMED, containment-owned, count 0. Cleanup by the receiver and then by the worker refuses with state unchanged; `close_outcome` reports CLOSED. **Absorption property:** 162 stale-identity calls across the seven round-2 terminal outcomes (28/28/26/28/24/14/14 per outcome) made **0 mutations** of state, completion, owner, count, charges or publications, raised no non-contract exception, and close reported CLOSED. The worker façade now exposes only `context_owner` and `run_effect` (R2 also had `revoke`) | **CLOSED** |
| P2-3 (OriginStateClosure-1) — `run_worker_cleanup` mutates before validating | IR7 (routine rewritten again under IR23) | Cleanup on a QUEUED command refuses unchanged. Third-task and issuing-task cleanup refuse with the full vector unchanged (`next_cleanup_step` stays 1). The true worker then runs steps 1 and 2 and exits success. Re-entrant cleanup inside an effect refuses; the effect returns with knowledge RETURNED and the step stays 1. (The new IR23 claim order causes a different defect, P2-9; that defect does not reopen this one) | **CLOSED** |
| P2-4 (OriginStateClosure-1) — queued removal has no exit receipt | IR5: CANCEL `NOT_BEGUN` receipt for every kind; delivery enters phase 1 in the same mutation | Two queued ranges. Cancel, and separately task loss, of the queued delivery command at serial 1 and at serial 2: each returns a `WorkerExitReceipt` and reaches (`retiring_handoff`, registration `retiring_refetch`, count 1) within the same call. The successor gets `refetch_required`. After stop, settlement returns `RefetchRequired` and replays idempotently; count 0, cursors (2,0) | **CLOSED** |
| P2-5 (OriginStateClosure-1) — barrier containment moves only the outer lease | IR4 + IR3 | **(a)** W's `run_plan_step`: `context_owner_mismatch`, state unchanged. **(b)** Accept after expiry: `context_expired`; the command becomes `quiescent_contained` and the lease containment-owned; the containment owner completes it alone (REFUSED, count 0). **(c)** Expiry at `settle_delivery_success`, and separately `revoke_generation` at PUBLICATION_READY, both reach (`retiring_handoff`, `retiring_refetch`, count 1). A SUCCESS receipt offered as the cause conflicts. Settlement returns `RefetchRequired`, count 0, cursors (2,0) | **CLOSED** |
| P2-6 (OriginStateClosure-1) — unusable refresh candidates get no §10 disposition | IR11 | **Neutral:** two candidates from one cursor. The first commit takes count 2→1. The diverged second returns `RefetchRequired`: lease REFUSED, count 0, 0 current candidates; a retry gets `RefreshRecordUnavailable`. **Nonquiescent:** stale candidate, its worker running, cursor moved. Result `RefreshContainmentPending` (contained, contained, count 1); further effects refuse; settlement before stop gets `lease_invalid`; after the exact stop `RefetchRequired`, REFUSED, count 0, read-only replay. **Changed variant:** same outcomes, with counts carrying the extra buffer permit (2→2→1). **DRAINING_OLD enqueue:** `RefetchRequired`, REFUSED, count 0, no leaked record; `begin_migration` then OK | **CLOSED** |
| P2-7 (OriginStateClosure-1) — unbounded history and O(history) lookups | IR13, design-scoped | **Executed contract lines** (`sys.settrace`): neutral commit 219/219/219 at history 10/200/1,500 (R2: 217 flat); delivery cycle 2,624 flat (R2: 2,618). The small rise is the new constant guards. **Retention:** 1,501 lease records with 0 non-empty ledgers and every per-command index empty; replay ring 9; the evicted receipt and candidate are garbage-collected; 0 buffer records | **CLOSED** |
| P3-1 (OriginStateClosure-1) — membership not bound to admission | IR9 | `request_leave` on an open runtime: `local_resource_draining`, member stays JOINED; `finalize_leave` refuses. After a proper close: LEFT, and admission and acquisition get `activation_required` | **CLOSED** |
| P3-2 (OriginStateClosure-1) — phase product not closed | IR17 | A second `begin_migration_effect` gets `migration_indeterminate` with the product unchanged; `retire_binding` gets `lifetime_protocol_required` (re-checked again in the phase-proof row below) | **CLOSED** |
| P3-3 (OriginStateClosure-1) — replay answers non-matching input | IR15 | A different failure gets `operation_outcome_conflict`, while the exact replay returns the same receipt. On a retiring handoff the exact cause replays, and fake or cross-lease causes conflict. A non-receiver accept replay gets `context_owner_mismatch` | **CLOSED** |
| P2-8 (OriginStateClosure-1-Reverdict) — join after local close; ghost member stalls migration | IR21 | **Unjoined registry, `start_close(runtime)`, graceful and hard:** `open_lifetime` refuses (`local_resource_draining`) with membership None. Participants stay 1→1, and join serial and activation are unchanged. `close_outcome` returns CLOSED via `close_unjoined`, and a later join refuses. The next attempt requires 1 member and acknowledges 1; `reopen_no_effect` and a fresh `begin_migration` both succeed. **Injected refusing `witness_local_close`** (an in-memory subclass of the reference coordinator): `close_outcome` refuses, and resource, descendant, admission and membership stay (local_draining, local_draining, draining, leave_pending). **R2 still produces the ghost:** participants 1→2; close refuses after its local commit; the next attempt requires 2 and acknowledges 1; reopen refuses; the deployment is stuck in DRAINING_OLD | **CLOSED** |
| P3-4 (OriginStateClosure-1-Reverdict) — terminal lease keeps the active serial; late delivery-stop setup raises | IR24 | `lease_facts` gives (refused, refused, containment, None, 0). A late `setup_reference_delivery_stop` replays the recorded observation. R2: active serial 1 and `IndexError` | **CLOSED** |
| P3-5 (OriginStateClosure-1-Reverdict) — post-acceptance cancel returns the SUCCESS receipt | IR27: deferred to W3 by operator decision | Unchanged on both trees: cancel after acceptance returns a `success`-kind receipt for EXECUTE and for a delivery, and presenting it as a delivery cause conflicts | **OPEN** (operator-deferred; non-blocking) |
| P3-6 (OriginStateClosure-1-Reverdict) — unconsumed initial candidates survive terminalization | IR26 | After 20 abandoned registrations: 0 initial-candidate records retained and 0 candidate identities alive (R2: 20 and 20). A later registration still works | **CLOSED** |
| P3-7 (OriginStateClosure-1-Reverdict) — close and barrier iterate every terminal record | IR28: deferred to W3 by operator decision | Still linear at 5/100/300 retired cycles (executed lines): `start_close` 113/1,158/3,358; `close_outcome` 199/2,479/7,279; `migration_queue_barrier` 209/3,344/9,944 | **OPEN** (operator-deferred; non-blocking) |
| Historical: ReviewState-3 P2-1 (worker exit) | RemPlan-2: original counterexample closed; root open through IR22 and IR23 | **Effect 1 raises** (`RuntimeError`, and separately a `BaseException` subclass):<br>- Inside the effect: lease RUNNING, command `effect_in_flight`, remaining {2}. A nested `run_effect(2)` refuses without consuming.<br>- After escape: CONTAINED, containment-owned, ordinals (∅,∅), BEGUN_UNCERTAIN, count 1.<br>- Effect 2, success, transfer, complete and publish all refuse, and pre-stop `complete_contained` gets `lease_invalid`.<br>- The late success records 1 diagnostic. After stop: REFUSED, count 0, publications 0.<br>**C1/C2 (workers W1, W2):**<br>- C2 refuses before C1 acceptance. Accept before stop and from the wrong task refuse; the receiver's accept works.<br>- C2 then dispatches with the outer lease still RUNNING and count 1 unchanged (no new permit).<br>- C1 replay returns the same receipt; C1 failure conflicts; C1 effect and dequeue refuse.<br>- A cross result refuses, dispatch beyond M refuses, and publication happens once (count 0).<br>**In-flight cancel and task loss:** each returns a receipt from inside the effect; the command is contained with BEGUN_UNCERTAIN; the other effect refuses; the late return is discarded; count 1 until stop; REFUSED, count 0 after | **Original sequence CLOSED.** The root is **open again through new P2-9** (cleanup/exit ordering, §5.3) |
| Historical: ReviewState-3 P2-2 (failed FIFO) | RemPlan root status: IR5, IR6 (State side); IR2, IR8 belong to other originators | **Literal sequence** (head accepted, successor queued, clock past expiry):<br>- Generic PUBLICATION step: `lease_invalid`, state unchanged (RUNNING, continuation, count 2).<br>- `prepare_delivery_publication`: `context_expired`, and phase 1 in that call (`retiring_handoff`, containment, count 2→1, cursors (2,0)).<br>- Generic `complete` gets `lease_owner_conflict`; `complete_contained` and success settlement get `operation_outcome_conflict`.<br>- The renewed-context successor dequeue gets `refetch_required`, and settlement before the delivery stop gets `lease_invalid`.<br>- After stop: `RefetchRequired`, equal replay, REFUSED, count 0, publications +0, cursors (2,0).<br>- A refresh on the retired registration refuses at candidate setup (`refetch_required`), leaving the caller's lease unchanged; the caller then completes it REFUSED, count 0. A new registration and its refresh work.<br>**Nine-cause matrix** (worker failure, expiry at commit, hard fence, receiver cancel, cleanup failure, receiver loss at PUBLICATION_READY, migration barrier, graceful close, `revoke_generation`):<br>- Each enters phase 1 within its triggering call, count 2→1.<br>- The successor never dequeues.<br>- Settlement refuses before stop, and the delivery stop refuses before the worker stop.<br>- A late success conflicts.<br>- After stop: `RefetchRequired` with idempotent replay, REFUSED, count 0, publications +0, cursors (2,0).<br>(P2-9 can turn the cleanup-failure cause into a delivered success; that is the P2-9 root, not a FIFO-order failure) | **CLOSED** (State side) |
| Historical: ReviewState-3 P2-3 (neutral refresh) | RemPlan root status: IR11, IR13 | **Neutral 0→1:** receipt, lease SUCCEEDED, count 1→0, publications +0, cursors (1,1), 0 queued, ring 1, 0 current candidates.<br>**Replays:** the candidate, receipt and `commit_refresh(receipt)` replays all return the same receipt.<br>**Next changed range:** delivered through 2, cursors (2,2), count 0.<br>**Provenance attacks:** fabricated, cross-registry and `None` identities get `RefreshRecordUnavailable`; copy, deepcopy and pickle raise `TypeError`.<br>**28 neutral commits behind an active head:** minimum count 1, sizes (1,1,9,9), cursors (29,0); on head success they fold to (29,29), count 0 | **CLOSED** |
| Historical: OriginStateClosure-2 State-Closure-P2-1 (phase proof) | Closed on MANIFEST-1; re-verify | The DRAINING proof is stale once the same attempt enters MIGRATING_PRE_EFFECT, and `begin_migration` returns the exact current request. The stale proof, stale request, fabricated, cross-coordinator and cross-attempt proofs all get `migration_indeterminate`. An early queue reopen raises. In every case the snapshot (state, generation, epoch, phase/serial/request, count, queue markers, membership) is unchanged. The exact current proof reopens once (epoch 2→3, after an earlier no-effect attempt). Its replay and the old proof then refuse; queues reopen only afterwards. After EFFECT_BEGUN, the pre-effect proof, a new proof and a second effect all refuse with the snapshot unchanged | **CLOSED** |
| Retained: initial 18, State-Supplement P2-1, expanded revocation | Unchanged requirements | **Permits:** forged and wrong-owner permit release raise `ValueError`, count unchanged, and migration gets `deadline_exceeded` while live.<br>**Close:** close with a queued buffer reports CLOSED, count 1→0, and a later dequeue refuses.<br>**Dequeue:** cross-registration, cross-admission and wrong-queue dequeue refuse with count and cursors unchanged.<br>**ACQUIRED publication:** refuses, unchanged.<br>**Expanded revocation** (accepted command, context invalidated, publish): `authority_invalid`, contained under the containment owner, publications 0; the containment owner completes it, count 0.<br>**Activation:** `recover_activation(None)` raises `TypeError`; wrong-fence withdrawal refuses; the exact withdrawal works once and then refuses; epoch reuse is refused. All three post-effect recovery outcomes are exact.<br>**Capability attacks:** a query plan as registration, a QUERY-only context, and direct ITERATOR_HANDOFF acquisition all refuse.<br>**Queued transfer:** an illegal queued transfer leaves state unchanged | **Holds** |
| Retained: correction-1 F2–F10 | Unchanged requirements | F2: later-before-earlier refuses; two FIFO successes reach (2,2), count 0. F3: same-fence withdrawal. F4: duplicate acknowledgement, acknowledgement after reopen, and count zero without every acknowledgement all refuse. F5: cross-lease gets `RefreshCommitRefused` with the other lease unchanged; fabricated gets unavailable; copy refuses. F6: one parent charge per resource, out-of-order refuses, replay and ordinal reissue refuse. F7: the recovery proof enforces the exact successor. F8: covered by the activation-recovery and post-effect set above. F9: issuing-task dequeue refuses unchanged. F10: a closed destination queue disposes `RefetchRequired`, REFUSED, publications +0, count 0 | **Holds** |

## Changed-range analysis

**What changed.** Exactly 8 MANIFEST-2 paths changed. I diffed each one against the Revision2 archive.

| File | Lines (Revision2 → now) | Lines added / removed |
|---|---|---|
| `lifetime_reference.py` | 2,009 → 2,074 | +89 / −24 |
| `worker_authority.py` | 143 → 144 | +8 / −7 |
| `snapshot_reference.py` | 181 → 186 | +5 / −0 |
| `lifetime.py` | 344 → 346 | +2 / −0 |
| `test_worker_exit_contracts.py` | 2,682 → 3,200 | +521 / −3 |
| `test_contract_source_rules.py` | 340 → 413 | +76 / −3 |

The other two changed paths are A16 and the implementation record. `generation_reference.py`, `buffer_reference.py`, `migration_reference.py`, `admission.py` and `authority.py` are byte-identical to Revision2.

**Per disposition near my findings.** Line numbers refer to MANIFEST-3.
- **IR21 (my P2-8).** It does what RemPlan-2 states.
  - What changed:
    - The `_runtime_close_begun` marker (248), set by `start_close` (1563), is checked by `_require_runtime_open` (325–337) inside `open_lifetime` (256) and `_admit` (305).
    - `start_close` relabels only legal admission edges (1564–1570), and witnesses drain and leave only for a JOINED member.
    - `close_outcome` validates every local precondition (1601–1610), then calls `close_unjoined` or `witness_local_close` before its first local mutation (1619–1625).
  - Verified behaviour: join after close begins refuses; an injected witness refusal leaves resources, admissions and membership unchanged.
  - No new stuck state. A repeated close is a no-op, hard close still contains every selected lease, peer-local close is unaffected, and P3-1 still holds.
- **IR22 (near my P2-2).** The façade `revoke` and `_revoke_worker_authorization` were removed. The 162-call absorption sweep and the queue-removal path hold. No regression.
- **IR23 (near my P2-3).** It closes its listed counterexamples.
  - What changed: the step is now claimed before the action runs (733–735); a re-entrant cleanup refuses (707); effect reservation refuses once cleanup has begun (588–591).
  - Verified behaviour: same-step and next-step re-entry and effect reservation during cleanup all refuse, and my P2-3 attacks still hold.
  - **Regression:** the success gate (664) was not updated to match the new claim order. A re-entrant success inside the final cleanup action now commits, which violates the IR23 design basis (§5.1/§5.3) and its own closure bullet ("success exit refuses ... until both steps have run"). This is filed as **P2-9**. Revision2 refused that success because its step advanced only in `finally` (Revision2 line 701).
- **IR24 (my P3-4).** `_discard_operation_history` clears the active serial (2006). `setup_reference_delivery_stop` replays or refuses on a terminal retirement (1470–1475). Closed.
- **IR25 (worker-exit replay neighbourhood).** The late-success worker check (652–656) works. A non-worker now refuses with `worker_authority_invalid` and diagnostic 0, where R2 recorded diagnostic 1. The worker's own late return still records exactly 1.
- **IR26 (my P3-6).** The changes:
  - `initial_candidate` field (127);
  - a replaced candidate is discarded at setup (1003–1008);
  - the field is cleared on consume (1058);
  - an unconsumed candidate is discarded at terminalization (2011–2013).

  `register_subscription` still refuses unknown or replaced candidates before mutation. Closed.
- **IR29.** The coordinator seam declares `recover_migration` (`lifetime.py` 328). The phase-product checks hold.
- **IR27 and IR28 (my P3-5 and P3-7).** Code unchanged by operator deferral; both still reproduce. **IR30:** tests only.

**Regression and new-root candidates.**
- **P2-9** (P2) is a regression of correction-1 behaviour inside the IR23 change. It is **bounded and not architectural**: the accepted design already fixes the order (§5.1, §5.3), and satisfying it needs no design, ownership or compatibility change.
- No other regression, stuck state or NEW ARCHITECTURAL root was found in the correction-2 neighbourhood of my findings.
- With the correction count at 2 of 2, the gate applies: the lane stops for the operator.

## 0. Evidence base

**Tuple verification.**

| Check | Expected | START (23:06 UTC) | END (23:29 UTC) |
|---|---|---:|---:|
| MANIFEST-3 self-hash | `9a9f8b2a…6af9` | match | match |
| MANIFEST-3 `shasum -a 256 -c` | 141 | 141 OK | 141 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | OK | OK |
| Legacy design / stopped source / old read-only / old product | 115 / 71 / 111 / 614 | OK | OK |
| AcceptanceEvidence / RemInputs / RemInputs-2 | 13 / 18 / 22 | OK | OK |
| MANIFEST-1 from inside `Revision1/garns` | 117 | 117 OK (`7e80ca67…`) | 117 OK |
| MANIFEST-2 from inside `Revision2/garns` | 128 | 128 OK (`ee441c18…`) | 128 OK |
| `.pyc` / `.pyo` / `__pycache__` | none | 0 | 0 |

These control hashes were identical at START and END:
- the round-3 prompt `0a85d320…` (verified before reading);
- my two reports (`d1add3b6…`, `43428228…`);
- RemPlan-2 `ab617c0f…`, DRAFT-3 `62e2ec64…`, Verification-3 `6d039448…`, VerificationLogs-3 `4b5677fc…` and BuilderPrompt-3 `dab49348…`.

MANIFEST-1 and MANIFEST-2 were never checked against the live source. There was no tuple movement.

**Read:**
- Controls: the round-3 prompt; RemPlan-2 in full (317 lines); DRAFT-3; Verification-3 in full; VerificationLogs-3 and BuilderPrompt-3 (skimmed); my round-1 and round-2 reports.
- Changed source: the diffs of all four changed source files against Revision2. In `lifetime_reference.py`, lines 186–2074 by region: every changed hunk plus the worker, delivery, refresh, close, barrier, containment and discard routines. Also `worker_authority.py` 95–144 and `snapshot_reference.py` 130–142.
- Unchanged source read for the historical roots: `generation_reference.py` 100–700, `buffer_reference.py` 440–500, the `recovery.py` proof classes and `values.py` `RefetchRequired`.
- Accepted design `W1A11-WorkerExitRedesign.md`: lines 278–300 (§4.2, §5.1) and 396–420 (§5.3).
- Fixtures and correction-2 tests:
  - `test_lifetime_contracts.py` 1–200;
  - `test_worker_exit_contracts.py` 40–75, 870–940, 1180–1210, 1538–1556, 1945–1956, 2715–2730 and 2942–3068 (CleanupClaimTests);
  - `test_admission_contracts.py` 1–95;
  - `test_generation_contracts.py` 25–62.

**Not read:**
- ReviewCode-3, ReviewState-3, ReviewCode-2-Reverdict, ReviewState-2-Reverdict, any `*-Reverdict-2.md`, or any round-3 prompt other than mine.
- One `rg -l` search listed the filename `ReviewState-3-Prompt.md` among its matches. I did not open it.
- Harness notices named other review agents in progress. I did not read their output and received no message from any reviewer.

**Suites** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`; all 12 commands exited 0):

| CPython | `-B -m unittest discover -s tests/contracts -t .` | `-B -m unittest discover -s tests -t .` | `-B tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | 187 OK | 290 OK (0 ResourceWarning lines) | 5 PASS |
| 3.12.12 | 187 OK | 290 OK (0) | 5 PASS |
| 3.13.12 | 187 OK | 290 OK (116 inherited, visible) | 5 PASS |
| 3.14.3 | 187 OK | 290 OK (140 inherited, visible) | 5 PASS |

**Inline attacks.** I ran about 30 inline `python3.14 -B` stdin attacks.
- **Comparison:** each counterexample that needed a before-state ran from identical script text in the Revision2 archive (round-2 findings, P2-9, IR25) or the Revision1 archive (round-1 findings), with each archive's own `tests/__init__.py`.
- **Private state:** I read private attributes (`_leases`, `_resources`, `_queues`, `_failures`, `_snapshots`) only to observe; none was written.
- **Test doubles:** the forged permit came from the coordinator's own identity issuer. The refusing witness was an in-memory subclass.
- **Prohibited actions:** no file was written, no helper was spawned, and no network was used. `tools/check.py`, `compileall` and `py_compile` were not run.
- **Harness errors:** three errors of my own were corrected and re-run: a P2-6 ordering mistake, bookkeeping `KeyError`s in a sweep, and an R2 `AttributeError` for the new `admission_state` observer. None came from the registry under test.
- **Other utilities:** besides the listed commands, I used `cat` (to hold a heredoc in a variable), `date`, `awk`, `grep`, `tr`, `cut`, `head`, `ls` and `sort`, all read-only.

## 1. Findings

### [P2-9] Correction 2 counts the final cleanup step as complete before its action returns, so a re-entrant success exit inside that action commits success; a later cleanup failure becomes only a diagnostic, and the result is accepted and published

**Root cause.** "Claimed" is conflated with "returned".
- `run_worker_cleanup` now claims the step before running the action (`next_cleanup_step += 1`).
- `worker_exit_success` still treats `next_cleanup_step > cleanup_steps` as "cleanup complete".
- The new `cleanup_in_progress` marker is consulted only by `run_worker_cleanup` itself.

**Location:** `src/garns/backends/contracts/lifetime_reference.py`:
- `worker_exit_success` 642–676; the only cleanup gate is at line 664.
- `run_worker_cleanup` 697–748: claim at 733–735, action at 737. In the handler (738–746), once an exit receipt exists, a cleanup failure only appends a diagnostic (745).
- `cleanup_in_progress`: declared at 155, set at 735 and cleared at 748; read only at 707.
- Revision2 advanced the step in `finally` after the action (Revision2 line 701), so the same re-entrant success was refused there.

**Violated invariant:**
- Design §5.1 (lines 294–295): every trusted cleanup completes before success exit is requested.
- Design §5.3 (lines 398–418):
  - success exit only after cleanup returns, so cleanup cannot fail once a publishable success receipt exists;
  - with no earlier error, the first cleanup failure is the primary exit, closes the result and transfers to containment.
- RemPlan-2 IR23: its design basis, which includes §4.2 re-entry refusal, and its closure bullet that success exit refuses and publications stay 0 until the cleanup steps have run.

**Reproduction** (identical script text, `python3.14 -B` stdin, MANIFEST-3 vs Revision2):
```
build_fixture(command_schedule_provider=lambda k: (WorkerCommandSpec("c", (1,), cleanup_steps=1),),
              assigned_worker_provider=lambda s: W, cleanup_provider=<action below>)
acquire EXECUTE (receiver A); dispatch; task := W; dequeue; run_effect(1); res := setup_reference_worker_result(...)
cleanup action (step 1): worker_exit_success(auth, res); then raise Fault (a BaseException subclass)
run_worker_cleanup(auth, 1)        -> Fault propagates
then: worker stop; task := A; accept_worker_result(receipt); LOWER; PUBLICATION

Revision2 : inner success -> Refusal worker_authority_invalid (state running_idle)
            after Fault: command contained, exit FAILURE (primary), diagnostics 0,
            lease contained / containment-owned, count 1, publications 0
MANIFEST-3: inner success -> WorkerExitReceipt (state success_pending inside the action)
            after Fault: command success_pending, exit SUCCESS, diagnostics 1, lease running / escrow-owned, count 1
            -> stop, accept OK, PUBLICATION OK: lease SUCCEEDED, count 0, publications 1
```

**Variants:**
- **Two-step schedule.** A re-entrant success inside step 1 refuses on both trees. Inside step 2 it commits on MANIFEST-3 only, so the window is exactly the final claimed step.
- **Delivery** (two-range handoff, one-step handoff schedule).
  - MANIFEST-3: success commits inside the final action, and the cleanup failure becomes diagnostic 1. After stop and acceptance, `settle_delivery_success` returns a settlement: SUCCEEDED, publications +1, cursors (1,1), count 0.
  - Revision2: the cleanup failure enters phase 1 (`retiring_handoff`), and success settlement conflicts.
- **Non-raising action.** Success is still committed while the cleanup frame is active, which breaks the order. The final state then matches the legitimate order.
- **Early stop.** If the executor also issues the worker stop inside the action, acceptance and publication complete before the action fails. This relies on the pre-existing residual that stop issuance does not consult `cleanup_in_progress`.
  - The late diagnostic is then filed against an already-discarded ledger, leaving one orphan `_failures` entry after terminalization.
  - Revision2 refuses every step of this variant.

**Impact:**
- **Fail-open:** an EXECUTE result or a delivered range is published, and its permit released, even though its trusted cleanup failed. The design's primary-failure path is bypassed: for EXECUTE a closed result and containment; for a delivery, phase 1 and `RefetchRequired`.
- **Regression:** correction-1 behaviour (Revision2) refused this.
- **Undetected by the suites:** CleanupClaimTests presents success exit only before and after cleanup steps, never from inside the final action.

**Classification:** P2, bounded, **not architectural**.
- Severity matches IR23 (a round-2 P2) and my P2-3 (IR7). The trigger class is the same: a trusted cleanup action that re-enters the registry.
- The consequence, publication after a *failed* cleanup, is at least as serious as IR23's publication after a *skipped* step.

**Required correction:** none is proposed. The correction count is 2 of 2; under the gate the lane stops and the operator decides between redesign and acceptance. Whatever the decision, any resolution must satisfy this invariant:
- A command's cleanup counts as complete only when every claimed step has **returned**.
- While a cleanup action is in progress, success exit (and any path that depends on cleanup completion) refuses and consumes nothing.
- A failure of the final step, with no earlier primary exit, remains the sole primary FAILURE.

**Closure test:**
- **Refusal:** with one- and two-step schedules, on EXECUTE and on a two-range delivery, a re-entrant `worker_exit_success` from inside the final cleanup action refuses with the full vector unchanged. The vector is: lease facts, publications, count, command state, ordinals, exit facts, effect knowledge and cleanup step.
- **Raise:** when that action then raises:
  - exit kind is FAILURE and the command is CONTAINED;
  - the lease is containment-owned (for a delivery: `retiring_handoff` with that failure as its cause);
  - publications stay 0;
  - after the exact stop: REFUSED (delivery: `RefetchRequired`), count 0.
- **Return:** when the action returns, success exit after the return proceeds and publishes exactly once.
- **Unchanged:** earlier-step behaviour and the existing CleanupClaimTests stay as they are.

## 2. Invariant analysis

These attacks held on MANIFEST-3:
- **Publication precondition.**
  - Coverage: every kind, the default and a distinct worker, zero dispatch, QUEUED, RUNNING_IDLE, inside an in-flight effect, SUCCESS_PENDING, QUIESCENT_SUCCESS, and after C1 of M=2.
  - Every refusal leaves the vector unchanged, and migration refuses while a command can run.
  - The exception is the illegitimate success P2-9 creates, which then passes this precondition legitimately.
- **Terminal absorption:** 162 stale-identity calls across seven terminal outcomes made zero mutations. A retiring handoff survives fence and revocation and settles once.
- **Refusals are mutation-free:**
  - wrong-task and issuing-task cleanup, and cleanup on QUEUED;
  - same-step and next-step cleanup re-entry, and cleanup inside effects;
  - effect reservation during and after cleanup;
  - the worker presenting itself as plan-step owner;
  - fake or cross causes on retiring handoffs;
  - non-receiver accept replay;
  - non-worker late success (IR25).
- **One containment routine:**
  - Queue removal returns a receipt and enters delivery phase 1 in the same call.
  - All nine FIFO causes enter phase 1 within the triggering call, with counts 2→1→0, cursors (2,0) and no successor crossing.
  - Accept-time expiry closes the result, and the containment owner completes alone.
- **Refresh:**
  - Quiescent divergence terminalizes and releases once; nonquiescent divergence stays contained until the exact stop.
  - A DRAINING_OLD enqueue is disposed of without a leak.
  - Disposed, evicted, fabricated and cross-registry identities get the uniform unavailable result.
  - Neutral lineage folds exactly behind an active head.
- **Bounded work and retention:** constant 219 lines per neutral commit and 2,624 per delivery cycle. The terminal tombstones (IR24, IR26) are consistent.
- **Membership and join:**
  - Join refuses once a runtime close has begun.
  - Close validates every precondition before its first local mutation; an injected witness refusal changes nothing.
  - Leave requires a witnessed drain, and LEFT cannot admit or acquire.
- **Phase product:** stale, fabricated, cross-coordinator and cross-attempt proofs refuse unchanged. The exact proof reopens once. EFFECT_BEGUN refuses pre-effect proofs. A second effect and CURRENT→RETIRED both refuse.
- **Retained obligations and suites:** the initial-18, supplement, expanded-revocation and F2–F10 obligations hold, and all suites pass on all four interpreters.

## 3. Risks and next action

**Residual risks below the bar:**
- **P3-5 and P3-7:** open and deferred by the operator to W3.
- **Illegal admission edge on close (pre-existing).** `close_outcome` still assigns RETIRED to every admission (1623–1625), so a DRAINING admission moves DRAINING→RETIRED, an edge outside overlay §3.1. It has no behavioural consequence, since both labels refuse. It is inconsistent with the new legal-edge comment in `start_close`.
- **Early stop issuance (pre-existing).** `setup_reference_worker_stop` (792–802) does not consult `cleanup_in_progress`, so a trusted executor that issues a stop while a cleanup frame is active is not refused. This amplifies P2-9.
- **Re-entrant failure exit (pre-existing in Revision2).** A re-entrant `worker_exit_failure` inside a cleanup action is accepted. This fails closed.
- **Unbounded outer records.** Terminal-lease, lifecycle-observation, delivery-stop and retirement records grow without bound. The design sets no bound on them.
- **Other originators' IDs.** Root-level closure of the historical roots also depends on IDs owned by other originators: IR2, IR8, IR10, IR12, IR14, IR16, IR18 and IR19.
- **Evidence limits.** This is deterministic single-process reference evidence. It proves nothing about real executor ordering, locks, durability, crash recovery or cross-process fencing.

**Next action:** stop the lane under the implementation gate. The correction count is 2 of 2 and the new P2-9 is open, so the operator decides between redesign and acceptance, with P2-9 and its invariant on the record. I propose no third correction.

For the operator's information only, not as a proposal: on any operator-directed tuple that meets the P2-9 closure test while every closure in this table still holds, my verdict would be GO.
