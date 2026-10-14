# W1A11-WorkerExitImplementation round 3 (correction 2 of 2) — STATE-AXIS REVIEW

**Review object:** The corrected worker-exit internal contracts and deterministic reference implementation after consolidated source correction 2 of 2. The implementation gate allows no further correction after this one.
- Approved filesystem tuple: `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256`, SHA-256 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9`, 141 entries. This is a filesystem tuple, not a Git commit.
- Controlling DRAFT-3: `62e2ec64f13b4aa9d9c878f097643ceb507e1dc8a66481aa102f559be13dede7`, with DRAFT-2 at `cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30`.
- Controlling dispositions: RemPlan-2 at `ab617c0f96c5436652090179b9a19834a88934c16163300be9e9fe18ae0a678f` and RemPlan at `a2d625e1c695b231b3e264470cbd61dfef1ed628744ec25255e59d37e366b2a1`.
- Status: unaccepted candidate. Implementation correction count is 2 of 2.
- Filed as `dev-docs/W1A11-WorkerExitImplementation-ReviewState-3.md`.

**Baseline:**
- Round-2 object: `dev-docs/W1A11-WorkerExitImplementation-Revision2/garns`, MANIFEST-2 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720`. Verified 128/128 from inside that archive.
- Round-1 object: `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns`, MANIFEST-1 `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544`. Verified 117/117 from inside that archive.
- 20-file writable baseline: map `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a`, 20/20.
- All sources were read directly from the filesystem at `/Volumes/projects/limbo/garns-wz/garns`, never from Git HEAD. Changed paths were compared with `cmp` and `diff -u` against both archives.
- Comparison probes ran with the working directory set to an archive. Each printed `garns.__file__`, which resolved into that archive's own `src`.

**Date:** 2026-10-05 (local). The UTC clock read 2026-10-04T23:39Z at the final END check.

**Axis:** State: durable-state semantics and adversity. I attacked state machines and restart legality, write ordering, kill points between writes, races and lock scope, and fail-closed direction. I treated recovery states as a closed grammar and hunted for new stuck states and false progress. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks (P2-1). Two P3 findings are filed and do not block. There are no P0 or P1 findings.
- **P2-1 is new in correction 2.** The IR23 change makes the success-exit gate count *claimed* cleanup steps rather than *completed* ones. A fixed hostile action on the final cleanup step can therefore commit success exit while cleanup is still on the stack. If the action then raises, the cleanup failure is demoted to a diagnostic and the operation publishes SUCCEEDED; an iterator delivery settles as success, folds its FIFO head and lets the successor dequeue. Revision2 and Revision1 both refused the same call.
- P2-1 is a bounded source repair. It is **not** a NEW ARCHITECTURAL root cause and needs no accepted-design, ownership or compatibility change.
- The correction count is 2 of 2. Under the implementation gate, a new P2 stops the lane for the operator's redesign-or-accept decision. This report does not propose a third correction.
- I re-ran the original counterexample of every root in IR1–IR19, IR21–IR26, IR29 and IR30. Each is closed on this tuple, and so are the original counterexamples of all five historical stopped roots. The worker-exit root stays OPEN through P2-1.
- **I pre-commit to GO on a revision that resolves P2-1 as specified, should the operator authorize one,** provided every closure recorded here still holds on that tuple.

---

## Prior-finding retrace table

"Re-run" means I executed the original reproduction, or its exact sequence through the current API, myself on this tuple. I used inline `-B` stdin probes with the repository fixtures. "R2" means the same script run from inside the Revision2 archive. Statuses are my State-axis retrace; closure by the originating reviewer remains theirs.

| Root (RemPlan) | Mapped round-1 IDs | Original counterexample re-run on this tuple | Status |
|---|---|---|---|
| IR1 publication precondition | ReviewCode-1 P2-1; OriginCodeClosure-1 P2-5; OriginStateClosure-1 P2-1 | **P1a** (M=2, publish after C1): `lease_invalid`, vector unchanged. After C2: one publication, `succeeded`, count 0; replay refused.<br>**P1b** (zero dispatch, EXECUTE and CONSISTENT_SNAPSHOT): refused, unchanged.<br>**P2-1(a)** (publish while `running_idle`): refused, unchanged.<br>**(b)** publish and `begin_migration` from inside effect 1: `lease_invalid` / `deadline_exceeded`; count 1, publications 0; the effect returned.<br>**(c)/(d)** distinct worker running: `commit_refresh` and `publish_refresh_buffer` return `RefreshCommitRefused`, unchanged; migration refused.<br>**(e)** registration while running: refused, unchanged. | CLOSED |
| IR2 atomic registration | ReviewCode-1 P2-6; OriginCodeClosure-1 P2-7 | Registration after accept: `succeeded`, count 0 and one publication in one call. A later cancel is a no-op. `complete(SUCCEEDED)` replays; `complete(REFUSED)` gives `operation_outcome_conflict`. `begin_migration` then succeeds. | CLOSED |
| IR3 presentation refusals | ReviewCode-1 P2-4; OriginCodeClosure-1 P2-6; OriginStateClosure-1 P2-5(a) | Wrong-task `commit_refresh`, neutral and changed: `RefreshCommitRefused`, vector unchanged; the owner's retry commits once. A distinct worker presenting the owner on LOWER: `context_owner_mismatch`, unchanged. | CLOSED |
| IR4 one containment routine | ReviewCode-1 P2-2; OriginStateClosure-1 P2-5; ReviewState-1 P3-1 | **P2/P2b** (expiry or invalidation at accept): accept refused; command `quiescent_contained`, lease containment-owned. `complete_contained` with no receiver call gives `refused`, count 0.<br>**P6** (expiry at dequeue): serial 1 → `cancelled_confirmed`, serial 2 → `refused`.<br>**P2-5(c)** (expiry or invalidation at `settle_delivery_success`; `revoke_generation` at PUBLICATION_READY): `retiring_handoff`, count 1, registration `retiring_refetch`; settle gives `RefetchRequired`, count 0, delivered 0. | CLOSED |
| IR5 queue removal / registry-detected non-success | ReviewCode-1 P2-7; ReviewState-1 P2-4; OriginStateClosure-1 P2-4 | Queued delivery cancel at serial 1 and serial 2: `WorkerExitReceipt`, lease `retiring_handoff`, command `queue_removed`, count 2→1. Exact replay works. Successor dequeue gives `refetch_required`. Settle gives `RefetchRequired`, count 0, delivered 0.<br>Cancel and task loss at PUBLICATION_READY: retiring, count 1. A SUCCESS receipt offered as cause gets `operation_outcome_conflict`. | CLOSED |
| IR6 terminal absorption / retiring survival | OriginStateClosure-1 P2-2; ReviewState-1 P2-1 | **Probe B** (failure-caused and receiver-loss-caused), then `revoke_generation` and a hard subscription fence: the lease stays `retiring_handoff`. Settle gives `RefetchRequired`, count 0, registration `retired`, cursors (2,0); the subscription closes `closed`; `begin_migration` succeeds.<br>**P2-2(b)**: queued cancel, then cleanup, refuses unchanged; close reports CLOSED.<br>**Absorption sweep**: 234 entry calls over 7 terminal outcomes × 2 tasks, with 0 mutations, 0 non-contract exceptions and CLOSED every time. | CLOSED |
| IR7 cleanup validate-before-mutate | OriginCodeClosure-1 P2-4; OriginStateClosure-1 P2-3; ReviewState-1 P2-2 | QUEUED: receiver, third-task and worker cleanup all refuse, unchanged.<br>RUNNING_IDLE: receiver and third task refuse, unchanged; the worker runs.<br>Re-entrant cleanup inside an effect refuses; the effect returns with knowledge `returned`, ordinal 1 completed and the step unconsumed. | CLOSED (P2-1 lies in the IR23 claim change, not in IR7's validation) |
| IR8 later-slot dispatch | OriginCodeClosure-1 P2-1; ReviewCode-1 P3-2 | **N1** (C2 dispatch after a cancel): `lease_invalid`, unchanged; `complete_contained` gives `refused`, count 0.<br>**N2** (retired by migration, close, fence, receiver loss or overflow): C2 dispatch refuses with the vector unchanged; settle brings count to 0; migration proceeds.<br>**P4**: outer `running`, C2 `queued`. | CLOSED |
| IR9 registry-witnessed leave | OriginCodeClosure-1 P2-2; ReviewCode-1 P2-8, P3-1; ReviewState-1 P2-3, P2-5; OriginStateClosure-1 P3-1 | **C/R5**: direct `request_leave` gives `local_resource_draining`; `finalize_leave` refuses; membership `joined`, count 1.<br>**E/M1**: close during an attempt reports CLOSED with `leave_pending`; the barrier acknowledges; `left` after reopen. **E2**: repeated graceful or hard `start_close` is a no-op.<br>**O2–O4**: the UNRESOLVED runtime stays `leave_pending` across no-effect reopen, full-rollback recovery and cutover, and is included in the next attempt. It becomes `left` after its CLOSED outcome; the later attempt then requires only the peer. A LEFT member's admission and `request_leave` refuse. | CLOSED |
| IR10 coordinator seam | OriginCodeClosure-1 P2-3; ReviewCode-1 P3-6 | A stub without the membership members fails `isinstance`; the registry rejects it with `TypeError`; the reference coordinator conforms. | CLOSED |
| IR11 refresh disposition | ReviewCode-1 P2-5, P3-4; ReviewState-1 P2-6; OriginStateClosure-1 P2-6 | **H** (three refreshes from one cursor): `[NeutralRefreshReceipt, count 2] → [RefetchRequired, refused, count 1] → [RefetchRequired, refused, count 0]`; 0 candidates; replay gives `RefreshRecordUnavailable`.<br>**Worker-backed divergence**: `RefreshContainmentPending`; the effect then refuses; settle refuses before stop; after stop it gives `RefetchRequired`, replays identically, count 0.<br>**R3** (changed commit in DRAINING_OLD before or after the barrier): `RefetchRequired`, `refused`, count 0, 0 orphan records; `begin_migration` succeeds. | CLOSED |
| IR12 hard fence | ReviewCode-1 P2-3 | A hard fence after accept leaves the lease `contained` and containment-owned. `complete_contained` from another task gives `refused`, count 0; close reports CLOSED. | CLOSED |
| IR13 bounded retention | OriginStateClosure-1 P2-7 | 1,200 neutral commits on one registration: 58 Python call events per commit at histories 20, 100, 400 and 1,200. The first candidate and receipt are garbage-collected. All per-command indexes are empty; ring 9; count 0. | CLOSED as the RemPlan scopes it (IR28 deferred) |
| IR14 first join activates | ReviewCode-1 P3-5; OriginCodeClosure-1 P3-1 | A join before the handshake refuses (`active_unused`). The handshake leaves `active_unused` with 0 participants. The first join gives `active`. Withdrawal after the join refuses. | CLOSED |
| IR15 replay exactness | ReviewCode-1 P3-3; OriginCodeClosure-1 P3-2; OriginStateClosure-1 P3-3 | The same failure replays; a different failure conflicts; a late success conflicts and records 1 diagnostic. Accept replay from a non-receiver gives `context_owner_mismatch`. A delivery retirement replays only with the exact cause; a different cause conflicts. | CLOSED |
| IR16 enumeration / source rules | ReviewCode-1 P3-7; OriginCodeClosure-1 P3-3 | The rules pin the exact terminalizer and worker-entry sets. The 7×8 command and 6×11 product suites pass. My own 90-cell command enumeration, which adds two cleanup substates, and my 40-cell phase-product enumeration found exactly one illegal cell, P2-1's. | CLOSED as filed. The suite lacks the cleanup substates where P2-1 lives; that gap is part of P2-1's closure test |
| IR17 phase guard | OriginStateClosure-1 P3-2 | A second `begin_migration_effect` refuses with the product unchanged; `retire_binding` refuses. | CLOSED |
| IR18 handoff schedule validation | ReviewState-1 P3-2 | An invalid handoff schedule raises `ValueError` before the exchange. Count, permits, buffer permits, cursors and lease records are unchanged. | CLOSED |
| IR19 serial-1 label | ReviewState-1 P3-3 | Removal after LOWER gives `refused`; a pristine removal gives `cancelled_confirmed`; count 0 in both. | CLOSED |
| IR21 join after close begun | ReviewCode-2 P2-1; ReviewState-2 P2-1; OriginCodeClosure-1-Reverdict P2-8; OriginStateClosure-1-Reverdict P2-8; ReviewCode-1-Reverdict P3-8 | **J1–J7**, graceful and hard:<br>• `open_lifetime` refuses (`local_resource_draining`); membership `None`; participants, join serial and activation unchanged.<br>• Admission refuses.<br>• `close_outcome` reports CLOSED through `close_unjoined` (open record `left`); a repeat reports CLOSED; a later join refuses.<br>• The next attempt requires 1 member, and `begin_migration` proceeds on the live member's acknowledgement.<br>R2, same script: join accepted, close refused after LOCAL_CLOSED, and the ghost included in the attempt (required 2).<br>**Property**: barrier-missing and injected coordinator-witness refusals leave resources, admissions and membership unchanged (R2: changed). A repeated `start_close` keeps REVOKED and RETIRED (R2: relabels to DRAINING). | CLOSED. Sibling relabel by `revoke_generation`: P3-1, pre-existing |
| IR22 façade route | ReviewCode-2 P2-2 | 100 third-task calls (2 kinds × 5 stages × 10 entries) change nothing. The façade exposes only `run_effect` and `context_owner`. R2: the façade `revoke` mutated state in all 10 kind × stage cells. | CLOSED. Rule-strength residual: P3-2 |
| IR23 cleanup claim | ReviewState-2 P2-2 | Same-step re-entry refuses with the vector unchanged; actions run `[1, 2]`; step 2 runs (R2: nested call accepted, actions `[1, 1]`, step 2 refused). Next-step re-entry refuses. A raising action still consumes its step. Effect reservation refuses during and after cleanup. Seven cleanup schedules show no lost or doubled step, and the marker is always cleared.<br>**But** the closure clause "success exit refuses … until both steps have run" fails from inside the final step's action: **P2-1**. | Original counterexample CLOSED. **Root OPEN via new P2-1, introduced by this correction** |
| IR24 dangling active serial | ReviewCode-2 P3-2; ReviewState-2 P3-1; OriginStateClosure-1-Reverdict P3-4 | A settled delivery shows `lease_facts` `(refused, refused, containment, None, 0)`; a late delivery-stop setup replays the recorded observation. `complete_contained` leaves `(…, None, 0)`. R2: `(…, 1, 0)` and an `IndexError`. | CLOSED |
| IR25 late-return authority | ReviewCode-2 P3-1; ReviewState-2 P3-2 | Receiver and third-task late success leave the diagnostic count at 0→0. The worker's late return, twice, gives 1. R2: 0→1. | CLOSED |
| IR26 initial candidates | ReviewCode-2 P3-3; OriginStateClosure-1-Reverdict P3-6 | 50 abandoned registrations leave 0 live candidates, store size 0, count 0. R2: 50 alive. | CLOSED |
| IR29 seam exit | ReviewCode-2 P3-4 | A stub lacking `recover_migration` does not conform, and the member is declared. R2: the stub conforms. | CLOSED |
| IR30 issuing-task effect | ReviewCode-1-Reverdict P3-7 (partial) | Receiver and third-task `run_effect` refuse with the vector unchanged and zero effects; the worker runs once. | CLOSED |
| Historical: worker exit | ReviewState-3 P2-1 | Effect 1 raises a `BaseException` while effect 2 is unused. Before escape: contained, containment-owned, ordinals `(∅,∅)`, `BEGUN_UNCERTAIN`, count 1. Effect 2 and success refuse. `complete_contained` refuses before stop and gives `refused`, count 0, after it. | Original CLOSED. **Root OPEN via P2-1** (cleanup primacy) |
| Historical: failed FIFO | ReviewCode-3 P2-1; ReviewState-3 P2-2; FreshCodeClosure-2 P2-1 (+ ReviewCode-2 P2-2, ReviewState-2 P2-1) | Literal ReviewState-3 P2-2: expiry before publication gives `retiring_handoff`, count 1, cursors (2,0). Generic completion refuses. A renewed-context successor dequeue gives `refetch_required`. Settle gives `RefetchRequired`, count 0, cursors (2,0). A new registration starts at (0,0); a refresh on the retired registration refuses. Last-permit races (5 causes, both sides of the commit) hold. | CLOSED. FIFO settlement is correct; P2-1's delivery variant is a worker-exit defect upstream of settlement |
| Historical: participant lifecycle | ReviewCode-3 P2-2 | **Repro A**: preactivation admission and join refuse; 0 participants. **Repro B**: the closed peer becomes `left`; the later attempt has size 1; migration proceeds on the live acknowledgement. The IR21 path is closed. | CLOSED |
| Historical: neutral refresh | ReviewState-3 P2-3 | Neutral (0,1]: receipt, `succeeded`, count 0, +0 publications, 0 queued, cursors (1,1). Candidate and receipt replays are identical. The next changed range gives (2,1). | CLOSED |
| Historical: phase proof | OriginStateClosure-2 State-Closure-P2-1 | A stale DRAINING proof in `MIGRATING_PRE_EFFECT` refuses with state, epoch, product, count and queues unchanged. A fresh pre-effect proof reopens once (epoch 2); replay and the old proof refuse. EFFECT_BEGUN disables the edge (product enumeration). | CLOSED |

IR20 (G10), IR27 and IR28 are deferred by operator decision. They were not retraced as findings, and `tools/check.py` was not run.

## Changed-range analysis

**Against Revision2.** Exactly 8 MANIFEST-2 paths changed, all inside the 23-path allowlist. Their SHA-256 values and line counts match DRAFT-3's table.

| Path | Lines before → after | `diff` lines |
|---|---|---:|
| `lifetime_reference.py` | 2,009 → 2,074 | 113 |
| `worker_authority.py` | 143 → 144 | 15 |
| `snapshot_reference.py` | 181 → 186 | 5 |
| `lifetime.py` | 344 → 346 | 2 |
| `test_worker_exit_contracts.py` | 2,682 → 3,200 | 524 |
| `test_contract_source_rules.py` | 340 → 413 | 79 |
| A16 | 192 → 208 | 46 |
| implementation record | 222 → 262 | 98 |

- No MANIFEST-2 path was dropped.
- MANIFEST-3 adds 12 manager documents: BuilderPrompt-3, DRAFT-3, RemPlan-2, RemInputs-2, the six round-2 reports, Verification-3 and VerificationLogs-3.
- The other 15 allowlisted paths are byte-identical to Revision2, including `buffer_reference.py`, `generation_reference.py`, `migration_reference.py`, `admission.py`, `values.py`, the retained test modules and the ADR README.

**Cumulative against Revision1.** 14 paths changed: correction 1's 13 plus `worker_authority.py`. All 71 files under `src/`, `tests/` and `tools/` are pinned by MANIFEST-3 or ReadOnly. No bytecode exists.

**Source diff mapped to roots.** Every source change maps to a RemPlan-2 root:

- **IR21:**
  - `open_lifetime` calls `_require_runtime_open` before `join_runtime`.
  - `_admit` checks it too.
  - `start_close(runtime)` sets `_runtime_close_begun` and relabels only ADMITTED→DRAINING/REVOKED and DRAINING→REVOKED.
  - `close_outcome` validates, then calls `close_unjoined` or `witness_local_close`, then commits local resource and admission state.
- **IR22:** the façade `revoke` and `_revoke_worker_authorization` are deleted. A new source rule enumerates the public entries that reach `_contain_lease`.
- **IR23:** new fields `cleanup_begun` and `cleanup_in_progress` (154–155). The in-progress refusal is at 707–710; the step claim before the action at 733–735; the `finally` clears the marker at 747–748. `run_worker_effect` refuses after cleanup has begun (588–591).
- **IR24:** `active_command_serial` is cleared at discard (2006). A terminal late delivery-stop setup replays or refuses (1470–1475).
- **IR25:** the worker is checked before the diagnostic is recorded (655–656).
- **IR26:** `initial_candidate` field (127); `discard_initial` in `snapshot_reference.py`; called at setup (1005–1007) and at discard (2011–2013).
- **IR29:** the `recover_migration` protocol member.
- The only addition not named by a root is the label-only `admission_state` observer (339–345).

**New root-cause candidates:**

- **P2-1** was introduced by the IR23 change. It is a regression: Revision2 and Revision1 both refuse the reproduction. It is bounded, not architectural.
- **P3-2** was introduced with the IR22 source rule: the rule checks that a marker is present, not that it comes first.
- **P3-1** is pre-existing (identical on Revision2). It is the sibling of IR21's relabel fix.
- There is **no NEW ARCHITECTURAL root cause.** The lifetime registry remains the sole mutable owner, the buffer state its subledger and the coordinator the deployment domain.

## 0. Evidence base

**Reviewer provenance.** I am a fresh Claude subagent dispatched with model parameter `opus` (`claude-opus-5-5`), with no prior agent context. I verified my prompt's SHA-256 (`270ec309…6b29a`) before reading it, and it was unchanged at END.

**Tuple verification.** START ran before any source was read. END ran after the last probe, and again after the final document reading.

| Check | Expected | START | END |
|---|---|---:|---:|
| `shasum -a 256` MANIFEST-3 | `9a9f8b2a…6af9` | exact | exact |
| `shasum -a 256 -c` MANIFEST-3 | 141 OK | 141 OK | 141 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | OK | OK |
| Legacy WorkerExitRedesign-MANIFEST-3 / ContractAmendment-MANIFEST-3 / ContractAmendment-ReadOnly / ContractAmendment-ProductGuard | 115 / 71 / 111 / 614 | OK | OK |
| AcceptanceEvidence / RemInputs / RemInputs-2 | 13 / 18 / 22 | OK | OK |
| MANIFEST-1 inside `Revision1/garns` | 117 OK | 117 OK | 117 OK |
| MANIFEST-2 inside `Revision2/garns` | 128 OK | 128 OK | 128 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 | 0 |

I did not check MANIFEST-1 or MANIFEST-2 against live source. At END, no current-round report existed in `dev-docs/` (ReviewCode-3, ReviewState-3, any `*-2-Reverdict`, any `*-Reverdict-2`). I read none, and no peer prompt.

**Documents read completely:**
- Process: the review-loop `SKILL.md` and `references/review-prompt-template.md` (read from disk); `../AGENTS_GWZ.md`; product `AGENTS.md`; program plan §§15–18 (lines 767–859); the ExecutionBrief; `docs/PRODUCT_LAYOUT.md`.
- Controls:
  - the accepted design `W1A11-WorkerExitRedesign.md` (1,121 lines) and its ACCEPTANCE;
  - the W2 overlay `W2-AdmissionLifetimeRedesign.md` (853 lines) and the W2 composition ACCEPTANCE;
  - `W1-ACCEPTANCE.md`;
  - `W2-QueryPlanningDesign.md`: its section map, §1 and §§5.3–6 (lifetime clauses superseded by the overlay).
- Lane: RemPlan; RemPlan-2; DRAFT; DRAFT-2; DRAFT-3; BuilderPrompt-2; BuilderPrompt-3; Verification-2 and -3; VerificationLogs-2 and -3 (commands and result lines); the implementation record; A16.
- Stopped-source and design reports named by Inputs:
  - ContractAmendment: STOP, ReviewCode-3, ReviewState-3, FreshCodeClosure-2, OriginStateClosure-2, RemPlan, RemPlan-2;
  - WorkerExitRedesign: ReviewSafety-3, ReviewConsistency-3, OriginCodeClosure-3 with its Erratum, OriginStateClosure-3.
- Prior-round inputs: ReviewCode-1, ReviewState-1, OriginCodeClosure-1, OriginStateClosure-1, ReviewCode-2, ReviewState-2, and all four round-2 `*-Reverdict` reports.

**Source read:**
- `lifetime_reference.py` 1–2074 complete; `generation_reference.py` 1–689 complete; `worker_authority.py` complete.
- Unified diffs against Revision2 of all four changed source files.
- `lifetime.py`: the local-transition table and protocol.
- Tests:
  - `test_worker_exit_contracts.py`: the correction-2 classes (2709–3200) completely; helpers at 1–140, 876–1042, 1182–1230, 1540–1560, 1947–1960 and 2211–2232; its full diff against Revision2.
  - `test_contract_source_rules.py`: lines 1–240 and its diff against Revision2.
  - Fixtures: `test_admission_contracts.py` 1–140 and `test_lifetime_contracts.py` 1–200.
- `recovery.py` proof shapes.
- `rg` found no private-attribute writes in the contract tests. The new hostile-witness test subclasses the coordinator as a trusted-setup fault seam.

**Gates.** Each interpreter ran with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B` and no warning filter.

| CPython | Focused `discover -s tests/contracts` | Full `discover -s tests` (ResourceWarning lines) | `tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.12.12 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.13.12 | Ran 187 OK | Ran 290 OK (108, visible) | 5 PASS |
| 3.14.3 | Ran 187 OK | Ran 290 OK (140, visible) | 5 PASS |

A passing suite is corroboration only. `tools/check.py`, `compileall` and `py_compile` were not run.

**Inline attacks.** I ran about 26 stdin `-B` probes on 3.14.3; P2-1 was also run on 3.11.14. Comparison runs used the Revision2 archive, and the Revision1 archive for P2-1. All drove real reference transitions through the repository fixtures. Private fields (`_participants`, `_attempts`, `_opens`, `_join_serial`, `_admissions`, `_leases`, `_authorizations`, `_buffers`, `_snapshots._initial`, `_queues` and similar) were read only to observe and never assigned. Clock, task and invalidation changes used only the fixtures' trusted provider seams, `authority.invalidate` and the `setup_reference_*` seams, exactly as the builder's tests do.

**Procedural disclosures.**
- Read-only utilities beyond the listed commands: `cat`, `grep`, `awk`, `sort`, `uniq`, `tr`, `cut`, `head`, `tail`, `ls`, `date`, `printf`, `basename` and shell loops. I used one `find /` to locate the review-loop skill.
- No file was written anywhere, including the scratchpad. No helpers, Git/GWZ, network, installs or services.
- Four of my probe scripts first failed through my own fixture misuse and were corrected:
  - a cleanup schedule applied to the registration kind;
  - the `MigrationRecoveryProof` signature;
  - `prepare_refresh` used for a peer subscription;
  - an f-string comparison evaluated after settlement in the first IR8 N2 run, which I re-ran with the comparison taken immediately.

## 1. Findings

### [P2-1] The success-exit gate counts claimed, not completed, cleanup steps, so success can commit inside the final cleanup action; a subsequent cleanup failure becomes a diagnostic and the operation publishes

**Location:** `src/garns/backends/contracts/lifetime_reference.py`.
- `worker_exit_success` (642–677): its only cleanup gate, at 664–665, is `if command.next_cleanup_step <= command.spec.cleanup_steps: refuse`. It never reads `cleanup_in_progress`, which only `run_worker_cleanup` reads (707).
- `run_worker_cleanup` (697–748) claims the step before the action runs (733–735). During the final step K, `next_cleanup_step` is therefore already K+1.
- Its `except BaseException` path (738–746) commits the cleanup failure as primary only when `command.exit_receipt is None`. Otherwise it appends a diagnostic.
- This was introduced by correction 2. Revision2 advanced `next_cleanup_step` only in `finally`, so the same call refused with "trusted cleanup schedule is incomplete".

**Violated invariant:**
- Design §5.1 (lines 294–295): "The outermost trusted worker wrapper performs every trusted cleanup before it requests success exit."
- Design §5.3 (lines 412–416): "Success exit is requested only after cleanup returns. Therefore cleanup cannot fail after a publishable success receipt exists. If cleanup raises after a result was privately computed and no earlier error exists, that first cleanup failure is primary … and transfers to containment."
- Design §8 (lines 596–598): "Cleanup that itself raises is the non-success cause if no earlier primary exists."
- Design §4.2 (lines 285–288): reentrant calls observe the in-progress state and refuse.
- Design §12 Consistency-1 P2-3 disposition (line 1017), "cleanup-only failure is primary", restated by the accepted design-closure reports, e.g. OriginStateClosure-3: "Success exit requires … completed trusted cleanup".
- RemPlan-2 IR23 closure (line 239): "Success exit refuses, and publications stay 0, until both steps have run."
- Fail-closed direction: this invents success.
- The documentation claims are false in this sequence: A16 lines 63–65 (cleanup failure preserves one primary exit) and implementation record line 152 ("success exit and publication wait for both steps").

**Reproduction.** Schedule `WorkerCommandSpec("c", (1,), cleanup_steps=K)` for K = 1 and K = 2, with distinct worker W. The fixed hostile cleanup action for step K calls `worker_exit_success(authorization, result)` and then optionally raises a `BaseException` subclass. This is the brief's sanctioned "fixed hostile … cleanup actions" model (ExecutionBrief lines 162–164; design §2 line 71). It is the same model as ReviewState-2 P2-2, which the lane rated P2. The sequence: LOWER, dispatch, dequeue, effect 1, cleanup steps 1..K; the executor issues stop after the frame exits; the receiver accepts; PUBLICATION.

```text
CURRENT (3.14.3)
raise_after=False: inner worker_exit_success during the final cleanup action -> ('ACCEPTED', 'WorkerExitReceipt') | cleanup returned
   after cleanup: (RUNNING, None, 'escrow', 1, 1) success_pending exit success diagnostics 0
   stop+accept+publish -> succeeded value value publications 1 count 0
raise_after=True:  inner worker_exit_success during the final cleanup action -> ('ACCEPTED', 'WorkerExitReceipt') | cleanup raised Fault
   after cleanup: (RUNNING, None, 'escrow', 1, 1) success_pending exit success diagnostics 1
   stop+accept+publish -> succeeded value value publications 1 count 0
CURRENT (3.11.14)  K=1 and K=2: inner=ACCEPTED exit=success diag=1 -> published succeeded pubs=1 count=0
REVISION2 (3.11.14) and REVISION1 (3.14.3), same script, K=1 and K=2:
   inner=REFUSED:worker_authority_invalid exit=failure diag=0 -> no publication; lease contained
```

Iterator-delivery variant (two-range handoff, `cleanup_steps=1` on ITERATOR_HANDOFF):

```text
CURRENT:   inner success exit ACCEPTED | exit success diag 1 | lease running count 2 cursors [2, 0]
           -> settle_delivery_success: succeeded count 1 cursors [2, 1] registration active -> successor range dequeued: acquired
REVISION2: inner success exit refused | exit failure | lease retiring_handoff count 1 | registration retiring_refetch cursors [2, 0]
```

**Grammar enumeration.** I enumerated 10 command states × 9 operations = 90 cells, including two new substates: "between cleanup steps" and "inside the final cleanup action". On this tuple, the only illegal accepted cell is `inside_final_cleanup × worker_exit_success → SUCCESS_PENDING`. On Revision2, the illegal cells were `between_cleanup × effect`, `inside_final_cleanup × effect` and `inside_final_cleanup × cleanup_next`. Correction 2 closed those three cells and opened this one.

**Impact:**
- A cleanup failure that should be the primary non-success becomes a diagnostic. A success receipt that design §5.3 says cannot exist yet is published, and the generation permit is released.
- For an iterator delivery, a handoff whose cleanup failed settles as success: publication, head fold, `delivered_through` advanced, successor dequeued. Under design §8 it should have entered two-phase retirement and refetch.
- No resumable work is concealed, because the stop is issued after the frame exits. This is false success, not a stuck state.
- The trigger requires a hostile or reentrant cleanup action, which is the same sanctioned model as IR23.

**Classification:** a new P2 introduced by correction 2 (a regression against Revision2 and Revision1). It is a bounded source repair, not architectural, and needs no accepted-design, ownership or compatibility change. Under the 2-of-2 gate it stops the lane for operator direction.

**Required correction** (a remedy specification, not a proposed third correction):
- The success-exit gate must require *completed* cleanup. It must refuse without mutation while `cleanup_in_progress` is set, or else track completed steps separately from the claim counter that orders steps.
- Whether `worker_exit_failure` should also refuse during an in-progress cleanup action may be decided with the same change. Today it commits a primary FAILURE there; that is fail-closed and pre-existing.

**Closure test:**
- Run K = 1 and K = 2, on EXECUTE and on a two-range delivery. The final-step hostile action's `worker_exit_success` must refuse with the full vector unchanged.
  - **(a)** If the action returns, the wrapper's success exit after the return succeeds and publishes exactly once.
  - **(b)** If the action raises, the cleanup failure is the primary FAILURE receipt. The lease is CONTAINED (or RETIRING_HANDOFF), publications stay 0, delivered progress is unchanged and the successor never dequeues. After stop, `complete_contained` or `settle_delivery_non_success` releases exactly once.
- Add both cleanup substates to `CommandGrammarEnumerationTests`.

### [P3-1] `revoke_generation` relabels RETIRED admissions to REVOKED, a backward edge out of the terminal admission state

**Location:** `lifetime_reference.py:1657-1659`. `revoke_generation` sets every admission to `REVOKED` unconditionally.

**Violated invariant:** Overlay §3.1 (lines 160–161) defines the legal record edges as `ADMITTED -> DRAINING -> REVOKED -> RETIRED` and `ADMITTED -> REVOKED -> RETIRED`; RETIRED is terminal (table line 154). RemPlan-2 IR21 removed this class of backward relabel for `start_close` (from the ReviewState-2 §3 note) but not for its sibling writer.

**Reproduction:**

```text
start_close(runtime): ['draining','draining'] -> close_outcome: closed ['retired','retired']
start_close after CLOSED: ['retired','retired']          (IR21 fix holds)
revoke_generation(): ['revoked','revoked']               (identical on Revision2)
```

**Impact:** The new `admission_state` observer reports REVOKED for an admission whose runtime is LOCAL_CLOSED, and a terminal record leaves its terminal state. Both labels refuse acquisition, so there is no state, count or ownership effect. This is a closed-grammar and diagnosability defect only. It is pre-existing and non-blocking.

**Correction:** relabel only ADMITTED and DRAINING to REVOKED; leave REVOKED and RETIRED unchanged.

**Closure test:** after a CLOSED runtime outcome, `revoke_generation` leaves every `admission_state` RETIRED, while live-lease containment and the registry epoch behave as before.

### [P3-2] The IR22 source rule checks that an authority marker is present, not that it precedes containment; one public containment entry contains before any receiver check

**Location:** `tests/contracts/test_contract_source_rules.py:59-79` (`AUTHORITY_MARKERS`, `CONTAINMENT_ENTRIES`) and `:197-205`. The rule passes if any marker string appears anywhere in the method or its direct private helpers.

Instance: `setup_reference_initial_snapshot` is classified "receiver" via the `self._lease_for_owner(` marker. For a caller-owned lease, `_lease_for_owner` → `_owner_matches` (`lifetime_reference.py:1738-1755`) compares only the owner object; it makes no current-task check. The seam's `_validate_queue_target` (986, which contains on mismatch at 2050) runs before the first presentation check in `_validate_barriers` (993).

**Violated invariant:** RemPlan-2 IR22 required "a source rule that enumerates every public method reaching `_contain_lease` and requires each one to validate a receiver, an assigned worker, or a trusted observation or barrier first". A16 line 194 and implementation record lines 98 and 181–182 claim the rule enforces "the authority each public containment entry validates first".

**Reproduction:**

```text
third task holding (lease, owner object) calls setup_reference_initial_snapshot with a mismatched queue:
REFUSED local_resource_fenced  (RUNNING, None, 'caller') -> (CONTAINED, None, 'containment')   (identical on Revision2)
```

**Impact:** The only current instance is a trusted fixture seam, so there is no production containment route. But the rule offered as IR22 closure evidence would accept a production entry that contains before authenticating, which is the IR3/IR22 defect class. The documentation overstates what the rule proves.

**Correction:**
- Make the rule order-sensitive: the first authority check must precede the first call that reaches `_contain_lease`.
- Either validate presentation before the seam's queue-target check, or classify trusted fixture seams explicitly.
- Correct the A16 and record wording.

**Closure test:** a synthetic entry that calls `_validate_queue_target` before any authority check fails the rule, and a third-task seam call leaves the lease unchanged.

## 2. Invariant analysis

The following attacks failed on this tuple. They are what the pre-commitment rests on.

- **IR21 join, admit and close ordering, and the coordinator witness.**
  - J1–J7, graceful and hard, as tabled.
  - Barrier-missing and injected witness refusals mutate nothing.
  - A repeated close never relabels RETIRED or REVOKED.
  - Graceful runtime close lets in-flight admitted work publish (`succeeded`), refuses new admission and acquisition, then reports CLOSED with the member `left`. Hard close contains the work and releases it once.
  - Two participants, 4 attempt endings (reopen, cutover, rollback recovery, success recovery) × 2 orders (close then acknowledge, acknowledge then close): in all 8 cases the closed participant can still acknowledge, becomes `left`, and the next attempt requires exactly the live peer. A closed runtime never became a permanent acknowledgement obligation.
- **Removed façade member.** 100 third-task calls across 10 entries × 5 stages × 2 kinds made zero state changes. No unauthenticated production route into containment remains (P3-2 concerns a fixture seam and rule strength).
- **Cleanup claim and marker, outside P2-1.**
  - Same-step and next-step re-entry refuse with the vector unchanged.
  - Actions run exactly `[1, 2]`; a raising action consumes its step.
  - Effect reservation refuses during and after cleanup.
  - Seven schedules (step raise, both raise, cancel before cleanup, cancel inside cleanup, cancel plus raise, failure exit inside cleanup, plain) show no lost or doubled step and the marker always cleared. Each schedule's primary and diagnostic grammar holds.
  - Cause injection inside a cleanup action, 2 kinds × 7 causes (cancel, task loss, expiry, invalidation, hard fence, revocation, migration barrier): containment or retirement, success refused, exactly one eventual release. The one exception is EXECUTE under a migration barrier, which is legitimate graceful old-generation completion.
- **Terminal discard (IR24, IR26).** 234 calls against 7 terminal outcomes from 2 tasks made no mutation and raised no non-contract exception. Every lease-level replay still answers from retained tombstones (settlement, retirement, lifecycle exit, late delivery stop). Command-level replay refuses after discard, per design §3.
- **Closed command grammar.** In the 90-cell enumeration, every other cell is legal or an idempotent replay or bounded diagnostic. In-effect failure, cancel and task loss each give `BEGUN_UNCERTAIN`, containment, count 1 and a refused effect return.
- **Phase product.** 40 cells: every illegal edge refuses with state, binding, epoch, product, count and participants unchanged. The stale DRAINING proof refuses; a fresh pre-effect proof reopens once; EFFECT_BEGUN disables the edge; generation 3 and same-generation requests refuse; an old buffer never resurrects after reopen (`admission_revoked`).
- **Last-permit iterator settlement.** Five causes (migration, close, hard fence, receiver loss, revocation):
  - Before the commit: `retiring_handoff`, count 1, delivered 0, late success conflicts, settle gives count 0.
  - After the commit: `(succeeded, 0, (1,1))` unchanged, replay returns the same object, late non-success conflicts.
  - No count of zero was ever observed with an unsettled head.
- **C1/C2 isolation.** Premature C2 dispatch refuses. In every C2 stage, C1 success and stop replays are idempotent, and C1 failure, effect, dequeue and cleanup attacks refuse with C2's vector unchanged. One publication; dispatch beyond M refuses.
- **Neutral lineage.** 30 neutral commits behind a delayed head: cursors (31,0), sizes (1,1,9,9), count 1. Evicted, cross-registry and counterfeit candidates and receipts all return `RefreshRecordUnavailable`; in-window replay is exact; A=1 ≤ L_refresh=1; the head folds to (32,32) with count 0. Changed-neutral-changed-neutral keeps two gaps and folds one span per success.
- **Retention.** Constant 58 call events per commit up to 1,200 history; evicted identities are collected.
- **Retained obligations.** All held:
  - F2: later-before-earlier refuses; two successes reach (2,2), count 0.
  - F7: exact successor only.
  - F9: issuing-task dequeue refuses.
  - F10: a closed target queue disposes `RefetchRequired`.
  - Initial State P2-1: forged or wrong-owner release raises, count unchanged.
  - Initial State P2-2: subscription close with a queued buffer reports CLOSED at count 0, and a later dequeue refuses.
- **Count zero never concealed resumable work** on any path I drove. Close remained local, and A7 UNRESOLVED stayed independent of worker stop and operation terminal state.
- **DRAFT-3 interpretations and limits, checked against the design:**
  - Façade `revoke` removed: matches §5.2's three trusted sources.
  - Witness-before-commit in `close_outcome`: the local phase cannot fail after validation, so this satisfies overlay §4 and A16's refusal rule as a declared reference limit.
  - `admission_state` is a provisional label observer.
  - The carried operator items are accurately listed: the refused `CURRENT × NONE → RETIRED` edge, IR27/IR28 deferred, A7 truth supplied by the caller.
  - The recorded mechanism "same-step re-entry is a step-unavailable refusal" is imprecise: during the action the in-progress check refuses first. The code and message are otherwise identical, with no consequence.
- **Test integrity.** The new tests drive real transitions. The hostile coordinator is a trusted-seam subclass. The single retained-test adaptation (façade `revoke` → structural absence) keeps its attack. No test writes private state.

## 3. Risks and next action

Residual risks below the finding bar (recorded, not filed):
- `commit_refresh` presented with the candidate of an already CONTAINED refresh applies the §10 disposition regardless of presenter, which is design-consistent for an invalidated operation. The owner's later exact `settle_contained_refresh(lease, stop)` then reports `operation_outcome_conflict` instead of replaying `RefetchRequired`. This is identical on Revision2.
- `_require_runtime_open` checks the close flag first, so a hard-fenced runtime refuses join and admission as `LOCAL_RESOURCE_DRAINING`; the FENCED branch is unreachable for a runtime.
- `worker_exit_failure` called inside a cleanup action takes the primary as a "body" failure. This is fail-closed and pre-existing.
- Carried below-bar items are unchanged: the spurious cancel diagnostic on double containment, the wrong-task `prepare_delivery_publication` refusal text, the queue relabel by the migration barrier, retained outer records, A7 truth supplied by the caller, and the refused `CURRENT × NONE → RETIRED` edge, which still needs an operator decision before W3/W4 rely on non-reuse from CURRENT.
- Deferred and not reported: production async, thread and process execution; locks; durability; crash recovery; provenance; PostgreSQL; activation; credentials; W3 names; IR20, IR27 and IR28.

**Single next action:** the lane owner files this NO-GO, and the lane **stops for the operator's redesign-or-accept decision**. Correction 2 of 2 is exhausted and this round reports a new P2. P2-1 is a bounded, non-architectural regression introduced by the IR23 change, with a one-gate remedy and the closure test specified above. Every other original counterexample I retraced is closed on this tuple.
