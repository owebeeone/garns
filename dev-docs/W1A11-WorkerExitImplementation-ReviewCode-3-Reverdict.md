# W1A11-WorkerExitImplementation (correction 3, MANIFEST-4): CODE-AXIS FOCUSED RE-VERDICT

**Object:** MANIFEST-4, the approved filesystem tuple `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-4.sha256`, SHA-256 `596c8ab80821646749a24fc63477d278a8b2f0ae1c145746c2a77255fb6e6339` (156 entries). It is not a Git commit.
- It is MANIFEST-3 after the operator-authorized one-line correction 3.
- MANIFEST-3's exact files are archived in `dev-docs/W1A11-WorkerExitImplementation-Revision3/garns`.

**Prior report:** `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-3.md`, SHA-256 `188c46684f97dd299c19e1b55780db8c589c4c64335dcd0183bc05186747a07a` (verified).

**Reviewer:** the same agent that wrote ReviewCode-3, with context intact. Claude Opus 5.5 (`claude-opus-5-5`), dispatched with model parameter `opus`.

**Axis:** Code. Focused re-verdict on P2-1 (IR31) and on the delta, as instructed by `…-Reverdict-3-Prompt.md` (SHA-256 `139563ca…151c`, verified at START and END). Independent, adversarial, read-only. Under the operator's two-reviewer rule, this is also the Code axis's full-review verdict of record for MANIFEST-4.

**Verdict: GO.**
- My P2-1 is **CLOSED** on MANIFEST-4. I re-ran all 8 variants (EXECUTE and two-range handoff × K=1 and K=2 × raising and non-raising) on Python 3.11.14 and 3.14.3.
- The delta is exactly the one described. I found no new P0–P2 in it or in the paths next to it.
- My two P3s are unaffected and stay open as non-blocking W3 items: IR32 (P3-1) and IR33 (P3-2).

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on MANIFEST-4 | Status |
|---|---|---|---|
| **P2-1** (IR31): in-frame success exit during the final cleanup action | RemPlan-3: the gate at `lifetime_reference.py:664` becomes `if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:` | See the vector table and paragraph below the table. | **CLOSED** |
| **P3-1** (IR32): the authority-first source rule checks marker presence, not precedence | Assigned to W3 (RemPlan-3) | `test_contract_source_rules.py` is byte-identical to Revision3. The in-memory mutant, with the `run_worker_cleanup` worker guard moved inside the containment `try`, still passes the per-entry check (`True`). | OPEN, non-blocking (W3) |
| **P3-2** (IR33): the cleanup-provider lookup comes before the step claim | Assigned to W3 (RemPlan-3) | Unchanged and identical on Revision3: a re-entrant provider gives nested `OK`, actions `[1, 1]`, step 2 refused, success accepted. The nested call finishes and clears `cleanup_in_progress` before the outer success, so the delta cannot reach it. | OPEN, non-blocking (W3) |

**P2-1 vector facts.** In every variant, on both interpreters, the in-frame `worker_exit_success` is refused (`worker_authority_invalid`), and the full `vector(...)` is identical before and after the call. Facts after the final cleanup returned or raised:

| Variant | Vector facts after cleanup | Outcome |
|---|---|---|
| EXECUTE, raising, K=1 / K=2 | lease `(contained, None, containment, 1, 1)`, publications 0, count 1, command `contained`, ordinals `([], [1])`, exit `(failure, receipt, 0 diagnostics, no cancel flag)`, knowledge `returned`, step K+1 | After the stop, `complete_contained` gives `refused`, publications 0, count 0 |
| EXECUTE, non-raising, K=1 / K=2 | lease `(running, None, worker, 1, 1)`, command `running_idle`, exit `(None, None, 0, False)`, step K+1 | Success exit afterwards is accepted once (replay returns the same receipt); accept returns `'v'`; publication gives `succeeded`, publications +1, count 0 |
| Handoff, raising, K=1 / K=2 | lease `(retiring_handoff, None, containment, 1, 1)`, count 2→1, primary `failure` with 0 diagnostics, cursors (2,0), lineage (1,0,0,9) | Successor dequeue gives `refetch_required`; settlement gives `RefetchRequired`, `refused`, count 0, cursors (2,0), publications unchanged |
| Handoff, non-raising, K=1 / K=2 | lease `running`, command `running_idle`, no exit recorded | One success afterwards; delivery settles `succeeded`, cursors (2,1), count 1 (the successor is still queued), publications +1 |

Revision3, same script: the in-frame call is `ACCEPTED`, the primary exit is `success` with 1 diagnostic, and the lease stays `running` in all four raising variants. That is the defect.

## Changed-range analysis

**The delta is exactly as described.** All 156 MANIFEST-4 paths were compared with the Revision3 archive:
- Exactly 3 MANIFEST-3 paths differ:
  - `lifetime_reference.py`: `diff` prints only `664c664`. The file is still 2,074 lines; SHA-256 `15abd5c2…bd703`.
  - `test_worker_exit_contracts.py`: +193 lines, none removed. It adds `CleanupInFlightSuccessExitTests` (3 methods, 5 subtests); SHA-256 `96b06244…bf7a`.
  - The implementation record: one row added at line 158; SHA-256 `f8b09086…bb5e`.
- 14 manager records are new in MANIFEST-4 and out of scope.
- `src/` and `tests/` hold 64 files on disk, all 64 pinned.
- Nothing else changed.

**Adjacent paths:**
- **Ordering in `worker_exit_success`.** The new condition sits after the state, reservation and required-effects checks, and before `_validate_worker_barriers` and every mutation on the success path. The unchanged vector on refusal confirms this.
- **Late-return branch.** It precedes the gate and is unchanged. Probe: a command contained mid-run, then a success request from inside its contained-before-stop cleanup action.
  - The receiver is refused (`worker_authority_invalid`), unchanged.
  - The worker gets `operation_outcome_conflict` with the bounded late-return diagnostic. The exit stays `cancel`, and no success receipt can be created.
  - Revision3 behaves identically.
  - This is design §4.1's diagnostic for a late worker return. The parenthetical in my round-3 remedy ("including the late-return diagnostic path") was broader than necessary, and P2-1's closure does not depend on it.
- **`run_worker_cleanup`.** It is byte-identical in content: claim before the action, the in-progress refusal, and the flag cleared in `finally`. The flag is set immediately before `try` and cleared in `finally`, so the new gate cannot leave a command permanently refused. `CleanupClaimTests` passes.
- **Worker-stop fixture.** The delta also closes a compound path. On Revision3, an in-frame success let `setup_reference_worker_stop` issue a stop (`SUCCESS_PENDING`) while the cleanup frame was still running. On MANIFEST-4 both calls are refused and the command stays `running_idle`. The out-of-scope behavior (a command contained mid-cleanup can still receive a fixture stop in-frame) is unchanged and identical on Revision3.

**Effect on my round-3 retrace table.** The only behavioral change is an added refusal of `worker_exit_success` while a cleanup action is running. Removing an accepted transition cannot reopen a closed counterexample, and none of my retrace counterexamples requested success inside a cleanup frame. Every round-3 closure carries over, and the full suites pass. The rows that P2-1 held open now close with it:
- IR23's closure criterion: success is refused while the final step runs and accepted once after it returns.
- The historical worker-exit root.
- The historical failed-FIFO root's cleanup-failure cause: a failing head now retires with delivered 0.

**No NEW ARCHITECTURAL root cause, and no new P0–P2.**

## Evidence base

**Tuple.** START was 2026-10-04T23:57:00Z and END 2026-10-05T00:00:20Z (UTC). Both were identical:

| Check | Result |
|---|---|
| MANIFEST-4 SHA-256 | `596c8ab8…6339` |
| MANIFEST-4 content | 156 OK |
| ReadOnly | 741 OK |
| RemInputs-3 | 13 OK |
| MANIFEST-3, from inside Revision3 | 141 OK (self-hash `9a9f8b2a…`) |
| `.pyc` / `.pyo` / `__pycache__` | 0 |

MANIFEST-3 was not checked against live source.

**Read:** the re-verdict prompt; RemPlan-3 (`7c21b5d5…`); DRAFT-4 (`cbd17c1b…`); BuilderPrompt-4; Verification-4 (`a312ebd1…`) and the result lines of VerificationLogs-4; the three diffs; `worker_exit_success` (lines 642–677); the new test class helpers.

**Not read:** ReviewState-3, any re-verdict, or any reviewer message.

**Suites.** All runs used `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, `-B` and no warning filter.

| CPython | Focused `discover -s tests/contracts` | Full `discover -s tests` | `tools/check_product.py` |
|---|---|---|---|
| 3.11.14 | Ran 190 OK | Ran 293 OK | 5 PASS |
| 3.14.3 | Ran 190 OK | Ran 293 OK (140 inherited ResourceWarning lines, visible) | 5 PASS |

The classes `CleanupInFlightSuccessExitTests`, `CleanupClaimTests` and `LateReturnAuthorityTests` also ran: 7 tests OK.

**Attacks.** Inline stdin `-B` scripts drove real fixture transitions. The P2-1 matrix ran on MANIFEST-4 on 3.14.3 and 3.11.14, with its raising variants also run against Revision3. The late-return, stop-fixture and provider probes ran on both MANIFEST-4 and Revision3. The P3-1 mutant is a pure in-memory AST check. Private state was read only, never assigned.

**Disclosures:** no file writes this time (every probe ran from stdin). No helpers, Git/GWZ, network, `tools/check.py`, `compileall` or `py_compile`.

## Findings

None new. P3-1 (IR32) and P3-2 (IR33) carry over unchanged and do not block.

## Risks and next action

**Below the bar:**
- The implementation record's status sentences are stale after the operator's exception: "no further correction is allowed after correction 2", and "Round-3 … remain mandatory". DRAFT-4 already discloses this.
- The record's IR23 row ("success exit and publication wait for both steps") is now accurate.
- The fixture stop for a command contained mid-cleanup is still out of scope per RemPlan-3.

**Next action:** the manager files this verbatim. GO on MANIFEST-4 from this axis. Under RemPlan-3's rule, acceptance as internal contracts and reference tests only also needs GO from the State re-checker. IR20, IR27, IR28 and IR32–IR34 go to W3, and the `CURRENT × NONE → RETIRED` edge goes to the operator.
