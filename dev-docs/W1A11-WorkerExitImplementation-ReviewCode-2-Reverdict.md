# W1A11-WorkerExitImplementation — ReviewCode-2 FINAL RE-VERDICT (CODE-AXIS)

**Review object:** MANIFEST-3 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9` (141 entries), the corrected candidate after correction 2 of 2 (the last). This is an approved filesystem tuple, not a Git commit. Date: 2026-10-05.
**Prior reports:** `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-2.md`, SHA-256 `b1488cc303170251f46981f2beb1881e5453941a7897bfa93da879c1aed857ab` (round 2, fresh full Code review of MANIFEST-2). I filed no round-1 report on this object.
**Reviewer:** The same agent that wrote ReviewCode-2, with context intact: a Claude subagent dispatched with model parameter `opus` (claude-opus-5-5).
**Axis:** Code. The axis covers interface contracts against call sites, ownership and visibility, compatibility with retained readers, error and hidden-mutation paths, and whether the diff does what its DRAFT claims and nothing the accepted design forbids. Focused final re-verdict; independent, adversarial, read-only. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new P2 (P2-3) blocks.
- All six findings I filed in round 2 (P2-1, P2-2, P3-1, P3-2, P3-3, P3-4) are **CLOSED** on MANIFEST-3. I re-ran each original counterexample.
- **P2-3** is a regression that correction 2 introduced in the IR23 cleanup-claim change, inside the `worker_exit_success` gate that my P3-1 also concerned. A success exit can now commit from inside the final cleanup action. A cleanup failure after it is then only a diagnostic, and the operation publishes `SUCCEEDED`. MANIFEST-2 refused this sequence.
- P2-3 is a bounded source defect and **not a NEW ARCHITECTURAL root cause**.
- The implementation correction count is 2 of 2. Under the gate, this NO-GO stops the lane for the operator's redesign-or-accept decision, and this report proposes no third correction. If the operator authorizes a revision, I pre-commit to GO on one that resolves P2-3 as specified.

---

## Prior-finding closure table

| ID (report) | Disposition claimed (root) | Verified on MANIFEST-3 | Status |
|---|---|---|---|
| P2-1 (ReviewCode-2) | **IR21.**<br>• `open_lifetime` calls `_require_runtime_open` (refuses once `_runtime_close_begun` is set or a RUNTIME resource has left `LOCAL_OPEN`).<br>• `_admit` applies the same guard.<br>• `close_outcome` validates locally, performs the coordinator witness (`close_unjoined` / `witness_local_close`) before its first local mutation, then commits.<br>• A repeated `start_close` relabels admissions only along legal edges. | Original sequence, graceful and hard: a second registry adds its runtime and calls `start_close(runtime)`, then `open_lifetime()`:<br>• the join gives `REF local_resource_draining`, membership `None`, and the coordinator's participants, join serial, activation and live member are unchanged;<br>• `close_outcome` gives `CLOSED`, the runtime is `local_closed`, and its open record is `left`;<br>• a later join refuses;<br>• the next attempt requires 1 member; `begin_migration` succeeds and no-effect reopen gives `current`.<br>Validate-then-commit: a hostile coordinator at trusted setup refuses `witness_local_close`, and `close_outcome` refuses with resources, admissions and membership unchanged (`('local_draining','local_draining',[],'leave_pending')`).<br>Repeated graceful plus hard close leaves admissions `retired`; graceful after hard leaves them `revoked`. | **CLOSED** |
| P2-2 (ReviewCode-2) | **IR22.** `revoke` and its slot are removed from `WorkerAuthorizationIssuer`; `_revoke_worker_authorization` is deleted. A source rule pins the 23 public containment entries and their authority markers. | The façade's public members are exactly `['context_owner', 'run_effect']`. A third task (neither receiver nor assigned worker) was tried at QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT (from inside the effect), SUCCESS_PENDING and QUIESCENT_SUCCESS on EXECUTE, and on a running two-range delivery:<br>• `worker_issuer.revoke` gives `AttributeError`;<br>• `request_worker_cancel` gives `context_owner_mismatch`;<br>• `run_worker_cleanup` and `worker_exit_failure` give `worker_authority_invalid` / `operation_outcome_conflict`;<br>• the full `vector(...)` is unchanged at every stage.<br>My independent AST call graph finds exactly the rule's 23 public methods transitively reaching `_contain_lease`. | **CLOSED** |
| P3-1 (ReviewCode-2) | **IR25.** `worker_exit_success` checks that the current task is the assigned worker before recording the late-return diagnostic. | On a receiver-contained command, third-task and receiver late success give `worker_authority_invalid` with the vector, including the diagnostic count, unchanged. The worker's late return gives `operation_outcome_conflict` with diagnostic 1, and a repeat leaves it at 1. | **CLOSED** |
| P3-2 (ReviewCode-2) | **IR24.** `_discard_operation_history` clears `active_command_serial`; on a terminal record, `setup_reference_delivery_stop` replays the recorded observation or refuses. | A running delivery retired by cancel, then stopped and settled, gives `lease_facts` = `(REFUSED, REFUSED, 'containment', None, 0)`. A late delivery-stop setup returns the recorded observation, both with a command and for a retirement with no command. EXECUTE after `complete_contained` gives `(…, None, 0)`. | **CLOSED** |
| P3-3 (ReviewCode-2) | **IR26.** `_LeaseRecord.initial_candidate` is set at setup, cleared at consumption, and discarded at terminalization through `ReferenceSnapshotRegistry.discard_initial`. | 50 abandoned registrations (candidate produced, then cancel) leave 0 retained initial records and 0 live candidate identities (weakref after `gc`). A later registration still delivers. | **CLOSED** |
| P3-4 (ReviewCode-2) | **IR29.** `SharedGenerationCoordinator.recover_migration` is declared and added to `COORDINATOR_METHODS` and `MEMBERSHIP_AND_PROOF_METHODS`. | `hasattr(SharedGenerationCoordinator, "recover_migration")` is `True`. A stub with every other declared member does not conform, and registry construction with it raises `TypeError`. The reference conforms. | **CLOSED** |

## Changed-range analysis

**Changed set.** Exactly 8 MANIFEST-2 paths changed, matching DRAFT-3 and Verification-3. All are inside the 23-path allowlist, and all 64 src/test files are pinned by MANIFEST-3.

| Path | Lines +/− | Size |
|---|---|---|
| `lifetime_reference.py` | +89/−24 | 2,009→2,074 |
| `worker_authority.py` | +8/−7 | 143→144 |
| `snapshot_reference.py` | +5/−0 | 181→186 |
| `lifetime.py` | +2/−0 | 344→346 |
| `test_worker_exit_contracts.py` | +521/−3 | 2,682→3,200 |
| `test_contract_source_rules.py` | +76/−3 | 340→413 |
| A16 | +31/−15 | 192→208 |
| implementation record | +69/−29 | 222→262 |

**Source dispositions near my findings.** The four source diffs were read in full against the Revision2 archive, and they do what RemPlan-2 states for IR21, IR22, IR24, IR25, IR26 and IR29. In particular, `close_outcome` is now validate-then-commit: every local precondition, then the refusable coordinator witness, then the local commit, which cannot fail.

**Regression in the IR23 change (P2-3).** IR23 moved the cleanup claim (`next_cleanup_step += 1`) ahead of the cleanup action (lines 733–735). `worker_exit_success` still reads `next_cleanup_step` as "steps completed" (line 664), and it does not consult the new `cleanup_in_progress` marker. On MANIFEST-2 the final cleanup action could not obtain a success exit; on MANIFEST-3 it can. This is a **new defect introduced by correction 2**, confirmed by running the same stdin script on both trees. It is a bounded source repair, **not architectural**.

**Benign changes and pre-existing behavior** (below the bar):
- A second `setup_reference_initial_snapshot` on the same lease now discards the first candidate. This is a small tightening beyond IR26; presenting the discarded candidate refuses without mutation.
- `open_lifetime` after a *hard* close reports `local_resource_draining`, not `local_resource_fenced`, because the flag check runs first.
- The record says a same-step cleanup re-entry gets a "step-unavailable" refusal, but the in-progress check runs first. Both are `worker_authority_invalid`.
- `close_outcome` still retires DRAINING admissions directly, a DRAINING→RETIRED label edge that overlay §3.1 does not list. This is pre-existing and has no behavioral effect.
- `add_resource` still accepts a child under a closing runtime. `close_outcome` then raises `ValueError` before any mutation; MANIFEST-2 raised after a partial mutation.

## 0. Evidence base

**Tuple verification (START and END identical):**

| Check | START | END |
|---|---|---|
| `shasum -a 256` MANIFEST-3 | `9a9f8b2a…6af9` | `9a9f8b2a…6af9` |
| `shasum -a 256 -c` MANIFEST-3 | 141 OK | 141 OK |
| Inputs / Baseline / ReadOnly | 31 / 20 / 741 | 31 / 20 / 741 |
| Legacy 115 / 71 / 111 / 614; AcceptanceEvidence 13 | all OK | all OK |
| RemInputs / RemInputs-2 | 18 / 22 | 18 / 22 |
| MANIFEST-1, from inside the Revision1 archive | 117 OK | 117 OK |
| MANIFEST-2, from inside the Revision2 archive (`ee441c18…0720`) | 128 OK | 128 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 |
| Prompt / RemPlan-2 / DRAFT-3 / my ReviewCode-2 | `0a85d320…54c5` / `ab617c0f…678f` / `62e2ec64…de7` / `b1488cc3…7ab` | unchanged |

No ReviewCode-3, ReviewState-3, `*-2-Reverdict.md` or `*-Reverdict-2.md` report for this object existed during the review, and none was read.

**Read:**
- This prompt in full (hash verified first).
- `RemPlan-2.md` in full, `DRAFT-3.md` in full, `BuilderPrompt-3.md` in full and `Verification-3.md` in full.
- `VerificationLogs-3.md`: commands and result lines for every run.
- The prior-round `ReviewState-2.md` in full; it independently found IR21 and recorded the IR23 notes.
- My own `ReviewCode-2.md`.
- Unified diffs against Revision2 of all four changed sources and of `test_contract_source_rules.py`.
- `CleanupClaimTests` (`test_worker_exit_contracts.py` 2942–3000).
- The A16 diff and lines 56–66; implementation record lines 95, 152 and 226–240.
- Current `lifetime_reference.py` lines 642–673.

**Not read:** the ReviewCode-3 and ReviewState-3 prompts, any other round-3 prompt, any current-round report or peer message, and the `*-1-Reverdict` reports. The last were not needed.

**Gates** (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B`, no warning filter). Corroboration only; none detects P2-3:

| CPython | Focused | Full (ResourceWarning lines) | `check_product.py` |
|---|---|---|---|
| 3.11.14 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.12.12 | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| 3.13.12 | Ran 187 OK | Ran 290 OK (114) | 5 PASS |
| 3.14.3 | Ran 187 OK | Ran 290 OK (140) | 5 PASS |

**Inline read-only attacks** (stdin `-B`, real transitions through the repository fixtures, on 3.14.3; P2-3 also on 3.11.14):
1. P2-1 graceful and hard sequences, with the migration and no-effect-reopen consequence.
2. The `close_outcome` hostile-witness property and admission relabel.
3. P2-2 third-task routes at six stages, plus an AST containment-route census.
4. P3-1 to P3-4.
5. The P2-3 cleanup-reentry matrix (`cleanup_steps` ∈ {1, 2} × action raises ∈ {yes, no}) on MANIFEST-3 and, with the identical script, inside the Revision2 archive (`garns.__file__` resolved into the archive).
6. The rest of the IR23 neighborhood.
7. Adjacent correction-1 re-checks.

Private fields were read only to observe (`_participants`, `_join_serial`, `_opens`, `_attempts`, `_admissions`, `_snapshots._initial`) and never assigned. Clock, task and cleanup behavior were set only through the fixtures' trusted provider seams.

**Procedural disclosure:** Besides the listed commands I used `ls`, `grep`, `awk`, `comm`, `sort`, `tr`, `cat`, `basename` and `echo`, read-only. One shell variable fed the same stdin script to both trees. The harness itself stored one large tool output (the ReviewState-2 listing) in its tool-results directory outside the product tree. I wrote no file. No helper, Git/GWZ operation, network, install, `tools/check.py`, `compileall` or `py_compile` was used.

## 1. Findings

### [P2-3] Correction 2's cleanup claim lets the final cleanup action commit a success exit; a cleanup failure after it is demoted to a diagnostic and the operation publishes SUCCEEDED

**Location:** `src/garns/backends/contracts/lifetime_reference.py`:
- 733–735: `run_worker_cleanup` claims the step (`next_cleanup_step += 1`, `cleanup_begun`, `cleanup_in_progress`) before the fixed action runs.
- 664–665: `worker_exit_success` gates on `next_cleanup_step <= spec.cleanup_steps`, so it treats a claimed, still-running final step as complete. It does not check `cleanup_in_progress`.
- 736–745: once an exit receipt exists, the cleanup failure handler only appends a bounded diagnostic.

**Violated invariant:**
- Design §5.3 lines 407 and 412–416: "if body and every cleanup step succeeded -> request success exit"; "Success exit is requested only after cleanup returns. Therefore cleanup cannot fail after a publishable success receipt exists. If cleanup raises after a result was privately computed and no earlier error exists, that first cleanup failure is primary, creates the sole exit receipt, closes/discards the result and transfers to containment."
- Design §5.1 lines 294–295: the wrapper "performs every trusted cleanup before it requests success exit".
- Design §4.2 nonreentrancy (lines 284–288), which IR23 extended to the cleanup stack.
- RemPlan-2 IR23 closure: "Success exit refuses, and publications stay 0, until both steps have run."
- A16 lines 58–65: cleanup failure preserves "one primary exit plus bounded diagnostics".

**Reproduction.** The same stdin script ran on both trees. The fixture uses `WorkerCommandSpec("c", (1,), cleanup_steps=K)`. A fixed hostile cleanup action is installed at trusted setup: the brief's sanctioned "fixed hostile … cleanup actions", the same method as IR23's own counterexample. The final step's action calls `worker_exit_success(authorization, result)` and then raises.

```text
MANIFEST-3 (3.14.3; identical on 3.11.14):
K=1 raises: inner success exit ('OK','WorkerExitReceipt') state inside action: success_pending | cleanup ('RAISED','RuntimeError')
            after: ('success_pending','success', diag 1, (RUNNING, None, 'escrow')) | stop+accept+PUBLICATION -> OK, 'succeeded', publications 1, count 0
K=2 raises: identical (success exit accepted inside step 2's action; publishes SUCCEEDED, count 0)
K=1/2 no raise: success exit accepted inside the action (success_pending before cleanup returned); publishes
Revision2 archive (MANIFEST-2), same script:
K=1/2 raises:   inner success exit ('REF','worker_authority_invalid') state inside: running_idle | cleanup RAISED
                after: ('contained','failure', diag 0, (CONTAINED, None, 'containment')) | no publication
K=1/2 no raise: inner refused; command running_idle; success only after the action returns
```

**Impact:**
- A trusted cleanup step that fails after a re-entrant success exit no longer becomes the primary exit.
- The command keeps its SUCCESS receipt and is accepted, and the operation publishes `SUCCEEDED` and releases its permit.
- This weakens below MANIFEST-2 the very guarantee IR23 was meant to strengthen: that every trusted cleanup completes before a publishable success. It contradicts A16 and the implementation record's IR23 row.
- `CleanupClaimTests` calls success exit only between cleanup steps, so all suites pass.

**Classification:** new defect introduced by correction 2 (regression relative to MANIFEST-2); bounded source repair; **not a NEW ARCHITECTURAL root cause**.

**Required correction** (for the operator's decision; the gate leaves no correction): before any mutation, `worker_exit_success` must refuse while `command.cleanup_in_progress` is set, or gate on completed rather than claimed cleanup steps.

**Closure test:**
- For K ∈ {1, 2}, a final-step hostile cleanup action calling `worker_exit_success` refuses with the full vector unchanged.
- When that action then raises, the cleanup failure is the primary FAILURE, the lease is `CONTAINED` under the containment owner, and publications stay 0.
- When it returns normally, success exit succeeds only after the action has returned.

## 2. Invariant analysis

These attacks held on MANIFEST-3:
- **Membership and close (IR21 neighborhood):**
  - joins and admissions refuse once close begins;
  - unjoined closes reach LEFT;
  - later attempts require only live members;
  - `close_outcome` refusals mutate nothing;
  - admissions never move backwards;
  - close during an attempt gives CLOSED with `leave_pending`, then `left` after reopen;
  - an A7-UNRESOLVED runtime stays `leave_pending` across reopen and leaves only after CLOSED.
- **Containment authority (IR22 neighborhood):**
  - no façade cancellation route remains;
  - every public containment entry validates a receiver, assigned worker, trusted observation or barrier;
  - every third-task attempt leaves the vector unchanged at all six stages.
- **Exit and diagnostic grammar (IR25 neighborhood):**
  - non-worker late returns refuse unchanged;
  - the worker's late return records one idempotent diagnostic;
  - a different failure conflicts.
- **Terminal discard (IR24/IR26 neighborhood):**
  - every checked terminal route leaves the active serial `None` and the ledger length 0;
  - a late delivery stop replays;
  - abandoned initial candidates die;
  - neutral commits stay at a constant 58 call events at histories 10, 100 and 300;
  - per-command indexes drain.
- **Seam:** the stub lacking `recover_migration` is refused; the reference conforms.
- **Rest of the IR23 neighborhood:**
  - same-step and next-step cleanup re-entry refuse;
  - effects refuse once cleanup has begun;
  - an early cleanup followed by failure exit contains, and `complete_contained` gives REFUSED, count 0;
  - re-entrant failure or cancel inside a cleanup action contains (fail-closed).

  The only gap is P2-3.
- **Adjacent correction-1 behaviors:**
  - **IR7:** wrong-caller cleanup refuses unchanged, and the genuine worker completes.
  - **IR4:** expiry at dequeue gives `cancelled_confirmed`, count 0; a fence at quiescent success gives `quiescent_contained`, and `complete_contained` succeeds.
  - **IR5:** a queued delivery cancel gives counts 2→1→0, delivered 0, and the successor refuses.

## 3. Risks and next action

**Residual risks below the bar:**
- IR27 and IR28 are deferred to W3 by operator decision.
- The refused design-legal `CURRENT × NONE → RETIRED × NONE` edge.
- A7 truth is supplied by the caller to `close_outcome`.
- The spurious cancel diagnostic on double containment.
- The DRAINING→RETIRED admission label edge.
- `add_resource` under a closing runtime blocks `close_outcome` (now with no partial mutation) until a repeat `start_close`.
- The hard-close join refusal code.
- The record's re-entry refusal-text detail.
- The source rule checks that authority markers are present, not that they come first. My probes found no ordering bypass.

**Single next action:** Per the implementation gate (2 of 2), this new P2 stops the lane. The operator decides redesign or acceptance with P2-3 known: a bounded source regression in `worker_exit_success` introduced by correction 2, not architectural. This report proposes no third correction.
