# W1A11-WorkerExitImplementation — ReviewState-2 FINAL RE-VERDICT (STATE-AXIS)

**Review object:** MANIFEST-3 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9` (141 entries). This is the corrected candidate after correction 2 of 2, an approved filesystem tuple, not a Git commit. Date: 2026-10-05.
**Prior reports:** `dev-docs/W1A11-WorkerExitImplementation-ReviewState-2.md`, SHA-256 `fdceadec6d24d27f8707e8b70acccae11f415f370f614f866d0b86e26c11b029` (round 2, fresh full State review). I filed no round-1 report on this object.
**Reviewer:** The same agent that wrote ReviewState-2, context intact; Claude Opus 5.5 (`claude-opus-5-5`).
**Axis:** State. I attack durable-state semantics and adversity: state machines and restart legality, write ordering, kill points between writes, races and lock scope, and fail-closed direction, treating recovery states as a closed grammar. Focused final re-verdict; independent, adversarial, read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new P2 (P2-3) blocks. Correction 2 introduced it in the IR23 cleanup neighbourhood, as a regression of correction-1 behaviour.
- All four findings I filed are CLOSED on MANIFEST-3 when their original counterexamples are re-run: P2-1 (IR21), P2-2 (IR23), P3-1 (IR24) and P3-2 (IR25).
- P2-3 is a bounded source defect, not a NEW ARCHITECTURAL root cause.
- The implementation correction count is 2 of 2, so under the gate this stops the lane for the operator's redesign-or-accept decision. I propose no third correction.

---

## Prior-finding closure table

| ID (report) | Disposition claimed (root) | Verified on MANIFEST-3 | Status |
|---|---|---|---|
| P2-1 (ReviewState-2) | **IR21.** `open_lifetime` and `_admit` refuse once runtime close has begun. `close_outcome` performs its coordinator witness before any local mutation. A repeated `start_close` never relabels admissions. | **Original sequence:** a peer is joined; a second registry, unjoined, runs `start_close(runtime)` graceful and, separately, hard.<br>• `open_lifetime` is refused (`local_resource_draining`). Membership stays `None`; the coordinator's (participants, join serial, activation) stay `(1, 1, active)`.<br>• `close_outcome` returns `closed` via `close_unjoined`, runtime `local_closed`. A later join is refused.<br>• The later attempt requires exactly the live peer. No-effect reopen and `begin_migration` both proceed on the live acknowledgement alone.<br>**Refusal paths are mutation-free:** a descendant added after the barrier raises `ValueError`, and a hostile coordinator refuses the witness; both leave resources, admissions and membership unchanged, with the runtime still `local_draining`.<br>**Admission relabel:** after CLOSED, a repeated graceful then hard close leaves admissions `retired, retired, retired`; hard then graceful leaves `revoked, revoked`.<br>**Revision2 archive still reproduces:** the join is accepted (participants 2), `close_outcome` commits then raises, and the ghost member blocks the reopen. | **CLOSED** |
| P2-2 (ReviewState-2) | **IR23.** The step is claimed before the action runs. An in-progress guard refuses re-entrant cleanup. Effect reservation is refused once cleanup has begun. | Same-step re-entry, next-step re-entry, and an effect reserved inside the action are each refused with (step, exit facts, lease facts, ordinals) unchanged.<br>• Actions run exactly `[1, 2]`.<br>• Success exit before step 2 is refused, publications 0; step 2 then runs.<br>• Effect after cleanup is refused; success after both steps succeeds.<br>**Revision2 still reproduces:** actions `[1, 1]`, success accepted before step 2, step 2 refused, effects accepted during cleanup.<br>One clause of this finding's closure test ("success exit refuses until both steps have run") still fails when success is re-entered from *inside* the last step's action. That has a different root cause, introduced by this fix, and is filed below as new **P2-3**. | **CLOSED** (original counterexample and root cause) |
| P3-1 (ReviewState-2) | **IR24.** Discard clears `active_command_serial`. A late delivery-stop setup on a settled retirement replays the recorded observation or refuses. | • A `complete_contained` terminal lease reports (active serial, ledger length) `(None, 0)`; the retired delivery also reports `(None, 0)`.<br>• A late `setup_reference_delivery_stop(retirement)` returns the recorded observation; observe replay succeeds; (facts, count, cursors) unchanged.<br>• Terminal replays still hold for delivery success, neutral commit, contained-refresh settlement and queue removal by task loss.<br>**Revision2:** `(1, 0)` and `IndexError`. | **CLOSED** |
| P3-2 (ReviewState-2) | **IR25.** The current assigned worker is validated before the late-return diagnostic is recorded. | With distinct worker W, after W's failure:<br>• receiver late success: refused `worker_authority_invalid`, diagnostic 0 → 0;<br>• third task: refused, 0 → 0;<br>• assigned worker: `operation_outcome_conflict`, 0 → 1; again, 1 → 1 (idempotent).<br>Lease facts unchanged throughout.<br>**Revision2:** the receiver fills the slot, 0 → 1. | **CLOSED** |

Two residuals from my round-2 §3 that RemPlan-2 folded in were also verified closed: the admission relabel (inside IR21) and effect reservation after cleanup began (inside IR23). A third §3 note became IR22, filed by ReviewCode-2: the façade now exposes only `run_effect` and `context_owner`, and `_revoke_worker_authorization` no longer exists.

## Changed-range analysis

**What changed.** MANIFEST-2 → MANIFEST-3 changes exactly the 8 paths declared in DRAFT-3: four contract sources, the two lane-specific test modules, A16 and the implementation record. Thirteen manager records were added. No path outside the allowlist changed. Diffs against the Revision2 archive, by area:
- **IR21 (`lifetime_reference.py`, 2,009 → 2,074 lines):**
  - new `_runtime_close_begun` flag;
  - `_require_runtime_open`, called from `open_lifetime` and `_admit`;
  - legal-edge-only admission relabel in `start_close`;
  - `close_outcome` reordered to validate, then witness at the coordinator (`close_unjoined` or `witness_local_close`), then mutate locally;
  - new `admission_state` observer.
- **IR22:** `revoke` removed from `WorkerAuthorizationIssuer`; `_revoke_worker_authorization` deleted.
- **IR23:** `run_worker_cleanup` sets `cleanup_in_progress`, claims the step (`next_cleanup_step += 1`, `cleanup_begun = True`) before the action, and refuses re-entry; `run_worker_effect` refuses reservation once `cleanup_begun` is set.
- **IR24:** `active_command_serial = None` at discard; the terminal delivery-stop fixture replays or refuses.
- **IR25:** current-worker check before the diagnostic.
- **IR26:** an `initial_candidate` lease field plus `ReferenceSnapshotRegistry.discard_initial`.
- **IR29:** `recover_migration` declared in `SharedGenerationCoordinator`.

**Coordinator-first ordering in `close_outcome` holds.** In the single-threaded reference it is safe: before the witness, the code refuses on any charged or `LOCAL_OPEN` resource in the selection. The only local transitions left after the witness are `LOCAL_DRAINING`/`LOCAL_FENCED → LOCAL_CLOSED` (legal edges) and the admission → RETIRED writes, none of which can fail. The probes confirm that every refusal path leaves state unchanged.

**New root-cause candidate: P2-3, a regression introduced by correction 2.** The IR23 fix moved the step increment ahead of the action, but the success gate in `worker_exit_success` still reads only that counter. During the *last* cleanup action the gate therefore already reads "cleanup complete". In correction 1 (Revision2) the counter advanced only after the action returned, so the same re-entrant success was refused. This is a bounded defect inside the existing owner and grammar, not a NEW ARCHITECTURAL root cause. I found no other regression near my findings: the correction-1 membership behaviours, terminal replays and the cleanup/close random walk all held.

## 0. Evidence base

**Tuple verification:** START 23:06:05Z, END 23:14:27Z, identical results.

| Check | Expected | START | END |
|---|---|---:|---:|
| `shasum -a 256 …MANIFEST-3.sha256` | `9a9f8b2a…6af9` | exact | exact |
| `shasum -a 256 -c …MANIFEST-3.sha256` | 141 OK | 141 OK | 141 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | 31 / 20 / 741 | 31 / 20 / 741 |
| Legacy 115 / 71 / 111 / 614; AcceptanceEvidence 13 | as stated | all OK | all OK |
| RemInputs / RemInputs-2 | 18 / 22 | 18 / 22 | 18 / 22 |
| MANIFEST-1 inside the Revision1 archive | 117 OK | 117 OK | 117 OK |
| MANIFEST-2 inside the Revision2 archive (self-hash `ee441c18…`) | 128 OK | 128 OK | 128 OK |
| This prompt SHA-256 | `0a85d320…54c5` | exact | exact |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 | 0 |

At END, no current-round report existed (no ReviewCode-3, ReviewState-3, `*-2-Reverdict` or `*-Reverdict-2`), and I read none and no other round-3 prompt. MANIFEST-1 and MANIFEST-2 were checked only inside their archives.

**Read:**
- this prompt;
- my ReviewState-2 report;
- RemPlan-2, DRAFT-3, BuilderPrompt-3 and Verification-3 in full;
- VerificationLogs-3 command and result lines;
- the accepted design §5.3 (lines 396–416), with §§4–9 as read in round 2;
- unified diffs of `lifetime_reference.py`, `worker_authority.py`, `lifetime.py` and `snapshot_reference.py` against Revision2;
- `test_worker_exit_contracts.py` CleanupClaimTests (2946–3000).

**Gates** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B`, no warning filter):

| CPython | Focused contracts | Full tests (ResourceWarning lines) | Product checks |
|---|---|---|---|
| 3.11.14 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.12.12 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.13.12 | Ran 187 OK | Ran 290 OK (114) | 5 PASS |
| 3.14.3 | Ran 187 OK | Ran 290 OK (140) | 5 PASS |

**Inline `-B` stdin probes** on 3.14.3. Each finding's probe was run on the live tree and, unchanged, inside the Revision2 archive (`garns.__file__` was confirmed per run). Key outputs:

```text
[graceful] open_lifetime: ('refused','local_resource_draining') | unchanged: True (None, 1, 1, 'active') ; close_outcome: closed | membership None
[hard]     open_lifetime: ('refused','local_resource_draining') | unchanged: True ; later attempt == live peer only: True ; reopen OK ; begin_migration OK
[same-step] nested -> refused unchanged=True | actions [1, 2] | success before step 2: refused pubs 0 | effect after cleanup: refused
P3-1 terminal facts (None, 0) | late delivery stop setup: OK (replays recorded observation) | unchanged: True
P3-2 receiver/third task: refused worker_authority_invalid, diagnostic 0 -> 0 ; assigned worker 0 -> 1 ; again 1 -> 1
exit attempted inside cleanup step 2 of 2: OK | step2 cleanup raised | cmd success_pending, diagnostics 1 -> lease succeeded, publications 1, count 0   (Revision2: refused; contained, pubs 0)
```

**Regression sweeps on MANIFEST-3.**
- Membership:
  - close during an attempt → `closed` + `leave_pending`, then `left` at reopen; repeat close is a no-op;
  - the UNRESOLVED runtime stays `leave_pending` across reopen, cutover and full-rollback recovery, then `left` after CLOSED;
  - direct `request_leave`/`finalize_leave` are refused;
  - a `left` member's `acquire_shared` and admission are refused.
- Random walk, 150 seeds × 500 steps: distinct worker, two-step cleanup, wrong-task attacks, hard fences, late success. 0 invariant breaks across 185 publications, 260 successes and 967 leases. The invariants added this round: terminal records hold no active serial or initial candidate, and no `cleanup_in_progress` survives outside an action.

**Disclosures.**
- No file was written: all probes went through stdin or shell variables.
- Read-only utilities beyond the allowed list were used for formatting only: `awk`, `sort`, `uniq`, `grep`, `ls`, `date`, `cut`, `tr`, `head`, `tail`, `basename`, `printf`, `python -c`.
- Private registry fields were read only to observe, never assigned.
- One probe injected a hostile coordinator at trusted setup. It rebound the test module's `ReferenceGenerationCoordinator` name to a subclass for the duration of a single `make_lifetime_fixture()` call, then restored it. No registry state was written.

## 1. Findings

### [P2-3] Correction 2 claims the cleanup step before the action runs, but the success gate reads only that counter. `worker_exit_success`, re-entered from inside the last cleanup action, is accepted, and a failure of that last step is demoted to a diagnostic on a publishable success

**Location:** `src/garns/backends/contracts/lifetime_reference.py`:
- 733–735: `run_worker_cleanup` advances `next_cleanup_step` and sets `cleanup_begun` and `cleanup_in_progress`, then runs the action at 737.
- 664–665: `worker_exit_success` refuses only when `next_cleanup_step <= cleanup_steps` and never consults `cleanup_in_progress`.
- 741–745: once any exit receipt exists, a later cleanup failure is recorded only as a diagnostic.
- 792–796: the stop fixture accepts SUCCESS_PENDING while a cleanup frame is still active, which lets the whole chain finish inside that frame.

**Violated invariant:**
- Design §5.3: "Success exit is requested only after cleanup returns. Therefore cleanup cannot fail after a publishable success receipt exists. If cleanup raises after a result was privately computed and no earlier error exists, that first cleanup failure is primary, creates the sole exit receipt, closes/discards the result and transfers to containment."
- Design §5.1: the wrapper performs every trusted cleanup before requesting success exit.
- Design §4.2: a callback-induced re-entrant call observes the in-progress state and refuses.
- RemPlan-2 IR23 closure: "Success exit refuses, and publications stay 0, until both steps have run."
- Fail-closed direction: a non-success becomes a published success.

**Reproduction.** Python 3.14.3; distinct worker W; schedule `WorkerCommandSpec("c", (1,), cleanup_steps=2)`. A fixed hostile cleanup action calls `worker_exit_success(authorization, result)`:

```text
exit attempted inside cleanup step 1 of 2: refused worker_authority_invalid | cmd running_idle, exit kind None, diagnostics 0
exit attempted inside cleanup step 2 of 2: OK WorkerExitReceipt | step 2 then raises | cmd success_pending, exit kind success, diagnostics 1
  -> the last cleanup step FAILED, yet stop/accept/publication: lease succeeded, publications 1, coordinator count 0
```

With a one-step schedule and the default worker:
- **Exit only:** success is accepted inside the action, and publication follows.
- **Exit, then the cleanup step raises:** the failure is only a diagnostic, and the operation publishes SUCCEEDED.
- **Whole chain inside the action, then the step raises:** stop, accept and publication all commit while the action is still on the stack (`('succeeded', 1, 0)`). The handler then records a diagnostic on the already-discarded command, leaving one `_failures` index entry behind for a terminal operation.

The same probe on the **Revision2 archive** refuses success inside the last action (`running_idle`), and the failing step becomes the primary FAILURE: lease `contained`, publications 0, count 1.

The suite does not cover this: CleanupClaimTests calls `worker_exit_success` only from outside the cleanup frame.

**Impact:**
- A command whose last trusted cleanup step fails can still exit success, publish SUCCEEDED and release its generation permit. The failure survives only as a diagnostic, which is exactly the state §5.3 says cannot exist.
- A non-idempotent cleanup that fails after the early success can leave uncleaned state behind a published result.
- An index entry outlives its operation.
- Severity follows ReviewState-2 P2-2: same hostile re-entry class, same consequence family.

**Classification:** bounded source defect introduced by correction 2, a regression of correction-1 behaviour. Not a NEW ARCHITECTURAL root cause: owner, seams and grammar are unchanged.

**Required correction** (recorded for the operator's redesign-or-accept decision; the gate allows no further correction and none is proposed here): `worker_exit_success` must refuse while any cleanup action of the command is on its stack (`cleanup_in_progress`), so the success gate requires every claimed step to have returned. The executor stop fixture should likewise refuse while a cleanup frame is active.

**Closure test:**
- A hostile last-step cleanup action that calls `worker_exit_success` is refused with the full vector unchanged.
- When that step then raises, its failure is the primary FAILURE receipt; the result is closed, the lease is contained, publications stay 0, and only REFUSED terminalization follows after stop.
- Success exit after both steps have returned still succeeds exactly once.

## 2. Invariant analysis

These attacks held on MANIFEST-3:

- **IR21 (my P2-1).**
  - A join after local close began is refused, graceful and hard, with membership and the coordinator unchanged.
  - An unjoined closing registry goes only `UNJOINED → LEFT`, and a later join is refused.
  - Later attempts contain only live members; reopen and migration proceed.
  - Every `close_outcome` refusal path is mutation-free, including the injected hostile witness refusal.
  - Admissions never move backwards.
  - The coordinator-first ordering cannot leave a half-committed close.
  - Correction-1 membership behaviour is preserved.
- **IR23 (my P2-2).**
  - Same-step and next-step re-entry are refused with no mutation; actions run `[1, 2]`.
  - Effect reservation is refused during and after cleanup.
  - Success exit is refused between steps when called from outside the cleanup frame.
  - The only gap is P2-3: success re-entered from inside the last action.
- **IR24 and IR26 (my P3-1).**
  - Every terminal route clears the active serial.
  - Terminal replays for delivery success and non-success, neutral commit, contained refresh and task loss still hold.
  - A late delivery stop replays.
  - Abandoned initial candidates are collected, and a later registration still delivers.
- **IR25 (my P3-2).** Only the assigned worker fills the diagnostic slot, and only once.
- **IR22 (my round-2 §3 residual).** The façade exposes only `run_effect` and `context_owner`.
- **Random walk.** 0 invariant breaks over 150 seeds, covering permit and buffer-permit conservation, the closed contained pairs and owner labels, terminal tombstones and index consistency.

## 3. Risks and next action

**Residual risks below the bar:**
- The cleanup `BaseException` handler records a diagnostic and a `_failures` index entry even after the lease went terminal while the cleanup frame was active. Besides the P2-3 chain, this is reachable through a fixture stop plus `complete_contained` inside a cleanup action (pre-existing fixture laxity).
- `_require_runtime_open` reports `local_resource_draining` even for a hard-fenced runtime, because the close-begun flag is checked first.
- `worker_cleanup_step` reports the claimed next step while that step's action is still running.
- Recorded and unchanged:
  - IR27 and IR28, deferred to W3;
  - the refused design-legal `CURRENT × NONE → RETIRED × NONE` edge;
  - caller-supplied A7 truth;
  - the spurious double-containment cancel diagnostic;
  - the queue relabel by the migration barrier;
  - retained outer terminal records.
- Deferred outcomes, not reported: production async/thread/process execution, locks, durability and crash recovery, provenance, PostgreSQL, activation, credentials, W3 names, and IR20.

**Single next action:** The implementation correction count is 2 of 2, so this new P2 stops the lane. The operator decides between redesign and acceptance. I propose no third correction.
