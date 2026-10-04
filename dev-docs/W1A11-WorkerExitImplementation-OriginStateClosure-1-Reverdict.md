# W1A11-WorkerExitImplementation — OriginStateClosure-1 RE-VERDICT (STATE-AXIS)

**Review object:** MANIFEST-2 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` (128 entries). This is the corrected candidate after consolidated source correction 1 of 2: an approved filesystem tuple at `/Volumes/projects/limbo/garns-wz/garns`, not a Git commit. Date: 2026-10-05 local (tuple checks on the UTC clock ran 15:03–15:24 on 2026-10-04).

**Prior report:** `dev-docs/W1A11-WorkerExitImplementation-OriginStateClosure-1.md`, SHA-256 `d1add3b62da7c0e1564bf227878dedb62058292e23f00fd3eece65bbed1888c2`.

**Reviewer:** Same agent as round 1: a Claude subagent, model `claude-opus-5-5`, dispatched with parameter "opus". My round-1 context is intact. The harness compacted the conversation between rounds, but the round-1 report, commands and outputs stayed available to me verbatim.

**Axis:** State: durable-state semantics and adversity. This is the originating State executable closure of my ten round-1 findings and of the historical stopped State roots. It is a focused re-verdict: independent, adversarial and read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new P2 blocks.
- All seven of my round-1 P2s and all three round-1 P3s are **CLOSED**. I re-ran each original counterexample on the corrected tuple, and on the Revision1 archive for the before-state.
- All four historical stopped State roots and their retained obligations hold.
- **New P2-8:** a never-joined runtime can join after its local close has begun. The resulting ghost member permanently stalls the next migration attempt. It is bounded and not architectural. Its trigger already existed in Revision1, and it sits in the IR9 neighbourhood.
- Four new P3s (P3-4 to P3-7) do not block.

I pre-commit to GO on a revision that resolves P2-8 as specified, provided the P2-1 to P2-7 closures and the historical-root retrace still hold on that tuple.

---

## Prior-finding closure table

"R1" is the same inline attack run from inside the Revision1 archive, where `garns.__file__` resolved into the archive. "Now" is the corrected tuple.

| ID | Disposition claimed (RemPlan root) | Verified on corrected tree | Status |
|---|---|---|---|
| P2-1 — publication bypasses the worker-exit ledger | IR1: one publication precondition on every non-delivery terminal success; zero-dispatch publication refuses; continuation-owner path for registration and refresh | **(a)** Default provider, PUBLICATION while the command is RUNNING_IDLE. R1: `succeeded … count=0 pubs=1`. Now: `lease_invalid`, every fact unchanged (`running … running_idle remaining=[1] count=1 pubs=0`). **(b)** Publication from inside effect 1, then migration. R1: publish OK, `begin_migration OK migrating` at count 0. Now: publish refused and `begin_migration deadline_exceeded` at count 1 in DRAINING_OLD. **(c)** Distinct worker W, neutral `commit_refresh` while W runs. R1: SUCCEEDED, count 0, MIGRATING. Now: `RefreshCommitRefused`, facts unchanged, migration refused. **(d)** Changed publish while running. R1: SUCCEEDED. Now: `RefreshCommitRefused`, unchanged. **(e)** Registration while running. R1: published, then no success path. Now: `lease_invalid`, no registration created. After acceptance it publishes, terminalizes SUCCEEDED and releases in one call (count 0, +1 registration); `complete(SUCCEEDED)` is idempotent, `REFUSED` conflicts, a later cancel is a no-op. **Zero-dispatch** EXECUTE publish refuses (R1: OK). **Stage matrix:** SUCCESS_PENDING and QUIESCENT_SUCCESS refuse (`lease_owner_conflict`, escrow-owned), and so does after C1 of M=2 (`lease_invalid`), each with all facts unchanged | **CLOSED** |
| P2-2 — containment writers revive terminal leases | IR6: terminal leases absorbing; retiring deliveries untouched | **(b) literal:** queue removal returns a receipt (R1: None); a cleanup call by the receiver, then by the worker, refuses unchanged; `close_outcome` reports CLOSED. R1 revived the lease to CONTAINED and stayed nonquiescent with count 0. **(a)/(c):** their triggers cannot be built because P2-1 is closed, so I ran the absorption property instead. 252 calls (18 entries × receiver and third task × 7 terminal outcomes: EXECUTE SUCCEEDED, contained REFUSED, CANCELLED_CONFIRMED, delivery RETIRED, delivery SUCCEEDED, neutral refresh SUCCEEDED, diverged refresh REFUSED) produced **0 mutations** of state, completion, owner, count, charges or publications, and close reports CLOSED. A retiring handoff survives `revoke_generation` and then settles (count 0) | **CLOSED** |
| P2-3 — `run_worker_cleanup` mutates before validating | IR7: validate before the containment scope; refusals consume no step | **(a)** Third task and issuing task refuse with the full vector unchanged (`next_cleanup_step` still 1). The true worker then runs steps 1 and 2 and exits success. R1: contained, with a success-exit conflict. **(b)** Cleanup on a QUEUED command refuses unchanged (R1: OK, step consumed). **(c)** Queue-removed command: see P2-2. Re-entrant cleanup inside an effect refuses, and the effect returns RETURNED (R1: OK) | **CLOSED** |
| P2-4 — queued removal has no exit receipt | IR5: CANCEL `NOT_BEGUN` receipt for every kind; delivery enters phase 1 in the same mutation | Two queued ranges; cancel and task loss of the queued delivery command at serial 1 and serial 2. Each returns a `WorkerExitReceipt` and leaves `retiring_handoff`, registration `retiring_refetch`, count 2→1 within the same call. The successor gets `refetch_required`. After stop, settlement returns `RefetchRequired` and replays idempotently; count 0, cursors (2,0). R1: returns None, stays `contained`/`active` at count 2, and `delivery_retirement` refuses | **CLOSED** |
| P2-5 — barrier containment moves only the outer lease | IR4, plus IR3 for the presentation half: one ledger-aware routine; presentation refusals mutation-free; accept requires escrow-owned RUNNING | **(a)** W's `run_plan_step` refuses `context_owner_mismatch` with state unchanged (R1: lease contained while the command ran). The later accept is an ordinary RUNNING→RUNNING continuation, so no CONTAINED→RUNNING edge is reachable. **(b)** Accept after expiry leaves the command `quiescent_contained` with the result closed, and the containment owner's `complete_contained` succeeds with no receiver action (R1: `lease_invalid`). **(c1)** Expiry at `settle_delivery_success` enters `retiring_handoff` with a registry cause, count 2→1; a SUCCESS receipt offered as the cause gets `operation_outcome_conflict` (R1: CONTAINED/active, and a SUCCESS cause accepted). **(c2)** `revoke_generation` at PUBLICATION_READY enters `retiring_handoff` and then settles to count 0 (R1: no retirement, no cause) | **CLOSED** |
| P2-6 — unusable refresh candidates get no §10 disposition | IR11: lineage, registration and coordinator checks inside guarded validation; every unusable outcome goes through `_dispose_refresh`; failed CANDIDATE discarded | **(a)** Two candidates from one cursor, neutral and changed. The diverged second commit returns `RefetchRequired`, lease REFUSED, count down once, 0 current candidates, 0 leaked records; a retry gets `RefreshRecordUnavailable`. R1: `refetch_required` raised while the lease stayed RUNNING and charged. **Nonquiescent variant** (candidate created before dispatch, worker running, cursor moved): `RefreshContainmentPending`; further effects refuse; settle refuses before stop; after the exact stop, `settle_contained_refresh` returns `RefetchRequired`, releases once, and replays read-only. **(b)** Changed commit during DRAINING_OLD before the barrier: `RefetchRequired`, REFUSED, count 0, no leak, and after the barrier `begin_migration` returns OK. R1: raised `generation_mismatch` with a leaked CANDIDATE, and migration was blocked | **CLOSED** |
| P2-7 — unbounded history and O(history) lookups | IR13, scoped to design §3 lines 127–128 and §10 lines 748–750 and 852–853; outer terminal-lease records not counted | **Executed contract lines (`sys.settrace`).** Neutral commit at history 10/200/1500: R1 213/973/6,173, Now **217/217/217**. Changed publish+dequeue+settle cycle at history 5/100/800: R1 2,370/9,590/62,790, Now **2,618/2,618/2,618**. **Wall time** at history 29→3,019: R1 24→126 µs, Now ~30 µs flat. **Retention:** the evicted first receipt and candidate are garbage-collected (R1: receipt retained); 0 non-empty ledgers; empty `_authorizations`/`_exit_receipts`/`_results`/`_failures`/`_stops`; buffer records pruned to 0 (R1: one per envelope). Residuals outside the RemPlan scope go to P3-6 and P3-7 | **CLOSED** (design-scoped closure criteria met) |
| P3-1 — membership not bound to admission | IR9 | `coordinator.request_leave` on an open runtime refuses (`local_resource_draining`) and the member stays JOINED; direct `finalize_leave` refuses. R1: LEAVE_PENDING → LEFT, then admitted again, and its queued buffer stalled migration. After a proper close: LEFT, a repeated close is a no-op, and a LEFT member cannot admit or `acquire_shared`. The new P2-8 also lies in this neighbourhood | **CLOSED** |
| P3-2 — phase product not closed | IR17 | A second `begin_migration_effect` refuses with serial and request unchanged (R1: OK and mutated). `retire_binding` refuses explicitly with `lifetime_protocol_required` | **CLOSED** |
| P3-3 — replay answers non-matching input | IR15 | A different failure gets `operation_outcome_conflict`, while the exact replay returns the same receipt. A retiring handoff with a fake or cross-lease cause gets a conflict. Accept replay from a non-receiver gets `context_owner_mismatch` (R1: OK for all three) | **CLOSED** |
| Historical: ReviewState-3 P2-1 (worker exit) | RemPlan root status OPEN: IR1, IR4, IR6, IR7, IR8 | Effect 1 raises as `RuntimeError` and as a `BaseException` subclass. Before escape: CONTAINED, containment-owned, ordinals `(∅,∅)`, `BEGUN_UNCERTAIN`, count 1. A nested `run_effect(2)` refuses without consuming. Effect 2, success, transfer, complete and publish all refuse. The late success records 1 bounded diagnostic. After stop: REFUSED, count 0. Accept before stop and accept from the wrong task refuse; the receiver's accept works. C2 refuses before C1 acceptance; afterwards C2 dispatches with the outer lease still RUNNING and no new permit. C1 replay, conflict, effect and dequeue attacks do not affect C2; a cross result refuses; dispatch beyond M refuses; publication happens once. In-flight cancel and task loss: `BEGUN_UNCERTAIN`, other effects refuse, the late return is discarded, release only after stop | **Original sequence CLOSED.** No State counterexample remains open in this root. IR8 belongs to OriginCodeClosure-1; I did not re-run its counterexample |
| Historical: ReviewState-3 P2-2 (failed FIFO) | RemPlan root status OPEN: IR5, IR6, IR8, IR2 | **Literal sequence:** expiry before PUBLICATION gets `lease_invalid`; generic `complete` and `complete_contained` refuse; the renewed-context successor dequeue refuses; cursors stay (2,0). Phase 1 drops count to 1; settlement refuses before stop; afterwards `RefetchRequired`, count 0, publications +0, idempotent replay; the retired registration refuses refresh; a new registration works. **Nine-cause matrix** (worker failure, expiry at commit, hard fence, receiver cancel, cleanup failure, receiver loss at PUBLICATION_READY, migration barrier, graceful close, `revoke_generation`): each enters phase 1 within the triggering call, counts 2→1→0, the successor never dequeues, settlement refuses before stop, a late success conflicts, cursors stay (2,0), publications +0 | **CLOSED** (State side; IR2 and IR8 belong to other originators) |
| Historical: ReviewState-3 P2-3 (neutral refresh) | RemPlan root status OPEN: IR11, IR13 | Neutral 0→1: receipt, lease SUCCEEDED, count 1→0, publications +0, cursors (1,1), 0 queued, ring 1. Candidate and receipt replays return the same receipt. The next changed range from 1 is delivered through 2. Fabricated and cross-registry identities get `RefreshRecordUnavailable`; copy and pickle refuse. 28 neutral commits behind an active head keep the count at ≥ 1 (sizes `(1,1,9,9)`) and fold to (29,29) on head success | **CLOSED** |
| Historical: OriginStateClosure-2 State-Closure-P2-1 (phase proof) | Closed on MANIFEST-1; re-verify | The DRAINING proof becomes stale once the same attempt enters `MIGRATING_PRE_EFFECT`; `begin_migration` now returns the exact current request. The stale proof, stale request, fabricated, cross-coordinator and cross-attempt variants all refuse with state, generation, epoch, phase/serial/request, count, queue markers and membership unchanged. The exact current proof reopens once (epoch 1→2), and replay or the old proof then refuses. Queues reopen only afterwards. After EFFECT_BEGUN the pre-effect proof and any new proof refuse unchanged | **CLOSED** |
| Retained: initial 18, State-Supplement P2-1, expanded revocation | Unchanged requirements | Forged or wrong-owner permit release raises `ValueError`, count unchanged, migration DEADLINE while live. Close with a queued buffer reports CLOSED, count 0, later dequeue refuses. Cross-registration and cross-admission dequeue refuse. ACQUIRED publication refuses. Expanded revocation (accepted command, context invalidated, publish) gets `authority_invalid`, contained under the containment owner, publications 0. Activation recovery: `recover(None)` TypeError; wrong-fence withdrawal refuses; the exact withdrawal works once; epoch reuse refused. All three post-effect outcomes are exact. Query, QUERY-context and iterator capability attacks refuse. Illegal queued transfer leaves state unchanged | **Holds** |
| Retained: correction-1 F2–F10 | Unchanged requirements | F2: later-before-earlier refuses; two FIFO successes reach (2,2), count 0. F3: same-fence withdrawal. F4: duplicate ack, ack after reopen, and count-zero-without-ack refuse. F5: cross-lease gets `RefreshCommitRefused`, fabricated gets unavailable, copy refuses. F6: one parent charge, ordered, no replay. F7: the recovery proof enforces the exact successor. F8: as above. F9: issuing-task dequeue refuses unchanged. F10: a closed destination queue refuses and contains, publications 0 | **Holds** |

## Changed-range analysis

**What changed.** Exactly 13 MANIFEST-1 paths changed: `lifetime_reference.py`, `generation_reference.py`, `lifetime.py`, `buffer_reference.py`, `snapshot_reference.py`, six contract test modules, A16 and the implementation record. `admission.py`, `authority.py`, `consumers.py`, `worker_authority.py`, `migration_reference.py`, `protocols.py`, `values.py`, `__init__.py`, `test_worker_authority.py` and the ADR README are byte-identical to Revision1.

The neighbourhood of my findings:
- `lifetime_reference.py` went from 1,780 to 2,009 lines (+558/−329):
  - `_publication_ready` (1641–1661) gates `run_plan_step` (401), `register_subscription` (969), `_commit_refresh_record` (1147) and `prepare_delivery_publication` (1328).
  - The single routine `_contain_lease` (1791–1881) is absorbing for terminal leases (1812) and leaves retiring leases alone (1814). It turns QUEUED into QUEUE_REMOVED with a CANCEL receipt and the serial-sensitive label (1820–1846). It contains running commands with history-derived knowledge (1847–1857). It closes SUCCESS_PENDING and QUIESCENT_SUCCESS (1858–1863). It routes deliveries into phase 1 with a registry-owned cause (1867–1878).
  - Presentation refusals precede barrier containment (1601–1604, 1631–1636).
  - Accept requires escrow-owned RUNNING (790–791).
  - `run_worker_cleanup` validates before its scope (660–701).
  - Refresh disposition is routed through `_dispose_refresh` (1101–1191, 1219–1240).
  - Indexed lookups plus `_discard_operation_history` (1925–1951).
- `generation_reference.py`: permits bound to member runtime and join serial; drain and close witnessed through the private open record (150–176); leave gated on those witnesses (177–196); buffer permits counted as obligations; a second migration effect refused; `retire_binding` refuses.
- `buffer_reference.py`: replay index, record pruning, `discard_candidate`, lineage clearing on retirement.
- `snapshot_reference.py`: a consumed initial candidate is deleted.

**Do the dispositions do what the RemPlan and design require?** For my roots, yes.
- The builder returns `RefreshCommitRefused` with no mutation when a *usable* candidate is presented before every slot is accepted. The RemPlan's IR1 text instead names `RefreshContainmentPending` for a worker that may resume. I judge the builder's choice compliant with design §10, which treats a presentation-only mismatch as unchanged-state refusal. No charge is released while the worker can resume, and *unusable* candidates still choose terminal or containment by worker quiescence (verified above).
- IR13's correction bullet "prune retired registrations" was not implemented. A constant-size retired tombstone is design-consistent (§8: known operations on a retired registration return typed `RefetchRequired`), so this does not reopen P2-7. The remaining iteration cost is filed as P3-7.

**New root-cause candidates** (all bounded; no NEW ARCHITECTURAL root cause; no accepted-design, ownership or compatibility change; no STOP):
- **P2-8:** join is not bound to the runtime's local open state. Close then commits locally before the coordinator witness can refuse. The trigger already existed in Revision1. The corrected IR9 claim "close_outcome validates before mutating" is incomplete on this path, which is now a refusal after local commit.
- **P3-4 to P3-7:** small, bounded defects found while checking the changed range.

The implementation correction count stays 1 of 2. P2-8 fits in correction 2.

## 0. Evidence base

**Tuple verification.** START was 15:03 UTC; END 15:23 UTC, re-checked at 15:24 UTC after the last probe.

| Check | Expected | START | END |
|---|---|---:|---:|
| MANIFEST-2 self-hash | `ee441c18…200720` | match | match |
| MANIFEST-2 `-c` | 128 | 128 OK | 128 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | OK | OK |
| Legacy design / stopped source / old read-only / old product | 115 / 71 / 111 / 614 | OK | OK |
| AcceptanceEvidence / RemInputs | 13 / 18 | OK | OK |
| MANIFEST-1 from inside the Revision1 archive | 117 | 117 OK (`7e80ca67…`) | 117 OK |
| `.pyc` / `.pyo` / `__pycache__` | none | 0 | 0 |

The re-verdict prompt (`2c64f44e…`), my round-1 report (`d1add3b6…`) and the RemPlan (`a2d625e1…`) were unchanged at both ends. MANIFEST-1 was never checked against the live corrected source. There was no tuple movement.

**Read:**
- The re-verdict prompt (hash verified first).
- The RemPlan (777 lines), DRAFT-2 (`cf10c9f6…`), BuilderPrompt-2 (`8f1bc939…`), Verification-2 (`506d6bb1…`) and the result sections of VerificationLogs-2 (`9cd61d67…`).
- The corrected `lifetime_reference.py` in full (lines 1–2009).
- Diffs against Revision1 of `generation_reference.py`, `buffer_reference.py` and `snapshot_reference.py`, the fixture diffs of `test_lifetime_contracts.py` and `test_admission_contracts.py`, and `prepare_refresh` in `test_worker_exit_contracts.py`.
- ReviewCode-1, ReviewState-1 and OriginCodeClosure-1, searched only to see whether join-after-close had already been filed. It had not; their probes C and E concern the related raise-after-mutation in close.

**Not read:** ReviewCode-2, ReviewState-2, any `*-Reverdict.md`, the ReviewCode-2/ReviewState-2 prompts, or any other round-2 prompt. I received no messages from other reviewers.

**Suites** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`):

| CPython | `-B -m unittest discover -s tests/contracts -t .` | `-B -m unittest discover -s tests -t .` | `-B tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | 173 OK | 276 OK (0 ResourceWarning lines) | 5 PASS |
| 3.12.12 | 173 OK | 276 OK (0) | 5 PASS |
| 3.13.12 | 173 OK | 276 OK (116 inherited, visible) | 5 PASS |
| 3.14.3 | 173 OK | 276 OK (84 inherited, visible) | 5 PASS |

**Inline attacks.** I ran 23 inline `-B` stdin attacks. Each original counterexample ran on both the Revision1 archive and the corrected tuple from the same script text.
- I read private attributes and the new `lease_facts` observer only to observe. No private state was written, no file was written, and no helper was spawned.
- `tools/check.py`, `compileall` and `py_compile` were not run.
- Besides the listed commands, I used `cat` (to hold a heredoc in a shell variable), `date`, `awk`, `sort`, `cut`, `tr`, `ls` and `head`, all read-only.

## 1. Findings

### [P2-8] A never-joined runtime can join after its local close has begun; close then commits locally, the coordinator witness refuses, and the JOINED ghost permanently stalls the next migration attempt

**Location:**
- `lifetime_reference.py` `open_lifetime` (247–252) has no local-state check. It calls `generation_reference.py` `join_runtime` (108), which validates only activation, deployment state and the absence of an attempt.
- `start_close` (1502–1512) witnesses drain only when a membership is already JOINED.
- `close_outcome` (1520–1551) commits LOCAL_CLOSED and RETIRED admissions (1535–1543), then calls `witness_local_close` (1550). That call refuses at `generation_reference.py:167` when drain was never witnessed.
- Nothing can remove the ghost afterwards: `request_leave` (182) and `finalize_leave` (186) require the private-open-record witnesses, while `begin_migration` (488) and `reopen_no_effect` (470) both require every frozen acknowledgement.

**Violated invariant:**
- Design §9 lines 657–663: join "validates … runtime identity and local open resource".
- Design §9 lines 677–680: closing before activation is `UNJOINED -> LEFT`, and "later open/join on that registry refuses".
- Design §9 lines 697–699: a closed runtime "can never become a permanent acknowledgement obligation".
- RemPlan IR9: "close_outcome validates before mutating"; overlay §4 and A16 require validate-then-commit.

**Reproduction** (corrected tuple; Revision1 produces the same ghost and stall, except its `close_outcome` returned CLOSED):
```
reg2 = ReferenceLifetimeRegistry(auth, object(), active_coordinator); add_resource(rt)   # UNJOINED
start_close(rt)            -> OK, rt local_draining (no membership, so no drain witness)
open_lifetime()            -> OK, membership JOINED                     # joins a closing runtime
close_outcome(rt)          -> Refusal local_resource_draining; rt now local_closed; membership joined
close_outcome(rt) again    -> Refusal local_resource_draining (refuses forever on retry)
(registry object discarded) coordinator.request_leave(ghost) -> Refusal; finalize_leave -> Refusal; state joined
next attempt: required 2 acked 1 | begin_migration Refusal deadline_exceeded
            | reopen_no_effect Refusal migration_indeterminate | state draining_old
live runtime acquire during the stuck attempt -> Refusal generation_mismatch
```
Recovery exists only while the same registry object survives: re-running `start_close(rt)` (which now witnesses drain), then `close_outcome`, reaches LEFT.

**Impact:**
- One open/close ordering race on a single runtime leaves a coordinator member that no transition can remove once its registry is gone.
- The next migration attempt can neither migrate nor reopen. Every participant stays in DRAINING_OLD and refuses new work.
- A close caller that retries loops on a refusal even though its resources were already marked LOCAL_CLOSED.

**Classification:** P2, bounded, not architectural, and no design change (the design already requires join to validate the local open resource). The trigger already existed in Revision1 and was not introduced by correction 1, but the corrected IR9 close path now refuses after its local commit.

**Required correction:**
- `open_lifetime`/`join_runtime` must refuse unless the runtime resource is LOCAL_OPEN and no local close has begun. Once `start_close` has run on an UNJOINED registry, only `close_unjoined → LEFT` is legal. One way: bind a close-begun marker to the open record.
- `close_outcome` must evaluate every coordinator precondition (membership state, witnessed drain) before committing LOCAL_CLOSED or RETIRED. A refusal must leave resources, admissions and membership unchanged.

**Closure test:**
- UNJOINED registry, then `start_close(runtime)`: `open_lifetime` refuses with the participant set, membership table and activation unchanged. `close_outcome` returns CLOSED via `close_unjoined → LEFT`.
- A later attempt requires exactly the live members, and both `begin_migration` and `reopen_no_effect` proceed.
- An injected coordinator-witness refusal leaves resources, admissions and membership unchanged.

### [P3-4] Terminalization keeps `active_command_serial` while discarding the ledger, so a late delivery-stop setup raises `IndexError`

**Location:**
- `_discard_operation_history` (1925–1951) empties `command_ledger` but leaves `active_command_serial` set.
- `setup_reference_delivery_stop` (1412) reaches the record through the retained retirement index and then indexes `command_ledger[active - 1]` (1417).
- `lease_facts` (899–923) reports the inconsistent tombstone.

**Reproduction:** cancel a delivery while its command runs, retire, stop and settle (REFUSED). `lease_facts` then gives `(REFUSED, REFUSED, 'containment', 1, 0)`: active serial 1 with an empty ledger. A second `setup_reference_delivery_stop(retirement)` raises `IndexError('list index out of range')`.

**Consequence:** a duplicated or late executor stop for a settled handoff crashes with a non-contract exception instead of an idempotent read or refusal, and the observer reports an active serial on a terminal lease.

**Fix:** clear the active serial at discard, or keep an explicit terminal marker. Delivery-stop setup on a terminal retirement then refuses or replays.
**Test:** a late stop setup after settlement refuses or replays, and no terminal lease reports an active serial.

### [P3-5] Cancellation and task loss after acceptance return the accepted command's SUCCESS receipt as their disposition

**Location:** `_contain_lease` takes its return value from `_active_exit` (1816). With no active command, `_active_exit` (1720–1723) returns the last command's receipt. This value is returned by `request_worker_cancel` (703–709) and `observe_receiving_task_done` (742–743).

**Reproduction:**
- EXECUTE after acceptance: cancel returns a `WorkerExitReceipt` of kind `success`.
- Delivery at PUBLICATION_READY: cancel returns the same kind, while phase 1 recorded a registry-issued failure as the cause. Presenting the returned receipt to `begin_delivery_non_success` gets `operation_outcome_conflict`.

**Consequence:** the design's "cancellation disposition" is reported as a success record, and the cause the registry actually recorded is not returned. This is a diagnosability defect.

**Fix:** after acceptance, return None or the registry-issued containment or cause record.
**Test:** post-acceptance cancel and task loss return a non-success disposition, and for a delivery it equals the recorded cause.

### [P3-6] Unconsumed initial-snapshot candidates survive their registration's terminalization

**Location:** `_discard_operation_history` (1925–1951) drops only refresh candidates. `snapshot_reference._initial` entries are deleted only by a successful `consume_initial` (133–136).

**Reproduction:** drive 50 registrations to an accepted command, then cancel and `complete_contained` each one (all REFUSED). `_snapshots._initial` then holds 50 records, with their frozen rows.

**Consequence:** abandoned registrations keep candidate records and row data for the life of the registry. This contradicts the implementation's "every current candidate field is discarded" claim and the RemPlan IR13 candidate bullet. There is no behavioral effect, because the leases are terminal.

**Fix:** discard the operation's unconsumed initial candidate at terminalization.
**Test:** after any non-successful registration, no initial-candidate record remains.

### [P3-7] Close, hard fence, migration barrier and revocation still iterate every outer terminal-lease record and retired-registration tombstone

**Location:**
- `close_outcome` (1526–1530), `start_close` (1516–1518), `migration_queue_barrier` (1560–1566) and `revoke_generation` (1586–1588) iterate the whole of `self._leases`.
- `buffer_reference.retire_for_resources` (422) iterates every registration ever created, including retired tombstones. RemPlan IR13's "prune retired registrations" was not implemented.

**Reproduction** (executed contract lines on the corrected tuple, for 5→100→400 retired cycles; Revision1 is similar, so this is pre-existing):

| Operation | 5 cycles | 100 cycles | 400 cycles |
|---|---:|---:|---:|
| `start_close(peer)` | 113 | 1,158 | 4,458 |
| `close_outcome(peer)` | 191 | 2,471 | 9,671 |
| `migration_queue_barrier` | 209 | 3,344 | 13,244 |

**Consequence:** close and migration-barrier cost grows linearly with lifetime history. This is outside the commit path that the design bounds, which is why it is a P3: the design sets no bound on outer records, and a retired tombstone is design-consistent.

**Fix:** sweep live-operation and live-registration indexes, or keep tombstones outside the iterated maps.
**Test:** the line counter shows constant close and barrier work as retired history grows.

## 2. Invariant analysis

These attacks held on the corrected tuple:
- **Publication precondition:** holds for every kind, with the default and a distinct worker, at zero dispatch, QUEUED, RUNNING_IDLE, inside an in-flight effect, SUCCESS_PENDING, QUIESCENT_SUCCESS, and after C1 of M=2. Every refusal leaves all facts unchanged. Migration keeps refusing while a command can run, and acceptance followed by publication succeeds exactly once.
- **Terminal absorption:** 252 stale-identity calls across seven terminal outcomes made zero mutations. A retiring handoff survives fence and revocation and settles once.
- **Refusals are mutation-free:**
  - wrong-task and issuing-task cleanup;
  - cleanup before dequeue;
  - re-entrant cleanup;
  - the worker presenting itself as plan-step owner;
  - fake or cross causes on retiring handoffs;
  - non-receiver accept replay.
- **No CONTAINED→RUNNING edge:** acceptance requires the escrow-owned RUNNING state.
- **One containment routine:**
  - queue removal returns a receipt and enters delivery phase 1 in the same call;
  - all nine FIFO causes enter phase 1 within the triggering call, with counts 2→1→0, delivered progress unchanged and no successor crossing;
  - accept-time expiry closes the result, and the containment owner completes alone.
- **Refresh disposition:** quiescent divergence terminalizes and releases once. Nonquiescent divergence contains until the exact stop. A DRAINING_OLD enqueue is disposed with no leak. Disposed and evicted identities get the uniform unavailable result.
- **Bounded work and retention:** constant 217 lines per neutral commit and 2,618 per delivery cycle. Evicted identities are collected, and per-command indexes are empty after terminalization.
- **Membership:** leave requires a witnessed drain, LEFT cannot admit or acquire, and a repeated close is a no-op. The one exception is the P2-8 join window.
- **Phase product:** the second effect and CURRENT→RETIRED both refuse.
- **History and suites:** all four historical State roots and the initial-18, supplement, expanded-revocation and F2–F10 obligations hold. All suites pass on all four interpreters.

## 3. Risks and next action

**Residual risks below the bar:**
- P3-4 to P3-7.
- Outer terminal-lease records and lifecycle-observation and retirement tombstones grow without bound. The design sets no bound on them, and the RemPlan scoped them out.
- Root-level closure of the historical roots also depends on IDs owned by other originators: IR2, IR8, IR10, IR12, IR14, IR16, IR18 and IR19. On the State-origin side, no original counterexample remains open.
- This is deterministic single-process reference evidence. It proves nothing about real executor ordering, locks, durability, crash recovery or cross-process fencing.

**Next action:** carry P2-8, and optionally P3-4 to P3-7, into consolidated correction 2 of 2 with the closure tests above. On that tuple I would then re-run the P2-8 sequence and re-check the P2-1 to P2-7 counterexamples and the historical-root retrace.
