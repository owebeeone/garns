# W1A11-WorkerExitImplementation — ReviewState-3 RE-VERDICT (STATE-AXIS), MANIFEST-4

**Object:** MANIFEST-4, `dev-docs/W1A11-WorkerExitImplementation-MANIFEST-4.sha256`, SHA-256 `596c8ab80821646749a24fc63477d278a8b2f0ae1c145746c2a77255fb6e6339`, 156 entries. This is the candidate after the one-line correction 3, which RemPlan-3 records as an operator exception to the exhausted two-correction gate. It is a filesystem tuple, not a Git commit. Reviewed 2026-10-05.

**Prior report:** `dev-docs/W1A11-WorkerExitImplementation-ReviewState-3.md`, SHA-256 `9a9637bc11a1ce32b3ac88f2c1f00548401e574f19adcab610d34bcd0d9625c2` (NO-GO: P2-1, plus P3-1 and P3-2).

**Reviewer:** the same agent as round 3, with context intact. Claude subagent, model `claude-opus-5-5`, dispatched with parameter `opus`. Re-verdict prompt `139563ca…2151c` was verified before reading and was unchanged at END.

**Axis:** State. This is a focused re-verdict and, under the two-reviewer rule, also the State full-review verdict of record for MANIFEST-4. Independent, adversarial, read-only.

**Verdict: GO** — P2-1 (RemPlan-3 IR31) is CLOSED on MANIFEST-4. I re-ran all 8 variants I filed on 3.14.3 and 3.11.14. I found no new P0–P2 in the delta or in the code next to it.
- The delta changes the outcome of exactly one of my 90 enumerated command-grammar cells, the P2-1 cell.
- My two P3s are untouched by the delta. They carry over, open and non-blocking, as IR34 and IR32, assigned to W3.

## Prior-finding closure table

| ID | Disposition claimed | Verified on MANIFEST-4 | Status |
|---|---|---|---|
| **P2-1** (IR31): success exit accepted inside the final cleanup action | Line 664 becomes `if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:` | All **8 variants**: K=1 and K=2 × raising and returning action × EXECUTE and two-range iterator handoff. In every one, the in-frame `worker_exit_success` gives `refused worker_authority_invalid` with the full `vector(...)` unchanged.<br>**Raising, EXECUTE:** lease `(contained, None, containment, 1, 1)`, command `contained`, exit `(failure, receipt, diag=0)`, knowledge `returned`, step K+1, pubs 0, count 1. After stop, `complete_contained` gives `refused`, pubs 0, count 0.<br>**Raising, delivery:** lease `(retiring_handoff, None, containment, 1, 1)`, command `contained`, exit `(failure, receipt, diag=0)`, count 2→1, cursors (2,0), pubs unchanged (3). The successor dequeue gives `refetch_required`. Settlement gives `RefetchRequired`, lease `refused`, count 0, cursors (2,0).<br>**Returning:** after cleanup, `running_idle` with exit `(None, None, 0, False)`. The post-return success exit is accepted once, and its replay returns the same receipt. EXECUTE publishes once (`succeeded`, pubs 1, count 0); delivery settles once (`succeeded`, count 1, cursors (2,1)).<br>3.11.14 gives identical outcomes.<br>Revision3, same script: the in-frame success is ACCEPTED, with the vector changed, in all 8 variants (the round-3 defect). | **CLOSED** |
| **P3-1** (IR34): `revoke_generation` relabels RETIRED → REVOKED | Assigned to W3; not part of correction 3 | `revoke_generation` (1657–1663) is byte-identical to Revision3; the delta cannot reach it. | OPEN (carried, non-blocking) |
| **P3-2** (IR32): the IR22 source rule checks marker presence, not order | Assigned to W3; not part of correction 3 | The source rule and `setup_reference_initial_snapshot` are byte-identical; `worker_exit_success` keeps its `_validate_worker_barriers(` marker; the rule passes. | OPEN (carried, non-blocking) |

## Changed-range analysis

**Delta against Revision3.** I compared all MANIFEST-4 entries with the archive. Exactly 3 MANIFEST-3 paths differ, matching DRAFT-4 and Verification-4:
- `lifetime_reference.py`: `diff` prints only `664c664`. The file is still 2,074 lines.
- `test_worker_exit_contracts.py`: 193 lines added and 0 removed. This is the new class `CleanupInFlightSuccessExitTests` (3 tests, 5 subtest cases), placed between `CleanupClaimTests` and `TerminalTombstoneTests`. It uses real transitions with no private-state writes, and its assertions run outside the cleanup action.
- The implementation record: one added IR31 row.
- The other 15 new entries are the archived MANIFEST-3 file and 14 manager documents (the round-3 reports, RemPlan-3, RemInputs-3, BuilderPrompt-4, DRAFT-4, Verification-4 and its logs). No entry was dropped. All files under `src/`, `tests/` and `tools/` are pinned. No bytecode exists.

**Reach of the change.** `cleanup_in_progress` is True only between the step claim (735) and the `finally` (748) of `run_worker_cleanup`, so the new predicate can alter only `worker_exit_success` calls made from inside a cleanup action. It is evaluated after pure checks and before any mutation or barrier containment.

**Nearby paths:**
- **Late-return branch** (649–659, ahead of the gate): identical on both trees. In a contained-before-stop cleanup frame, the worker's success gives `operation_outcome_conflict` and records one late-return diagnostic (design §4.1). The receiver and a third task are refused with the vector unchanged (IR25 holds).
- **`run_worker_cleanup`:** byte-identical.
- **Worker-stop fixture:**
  - In a body-running cleanup frame on MANIFEST-4, in-frame stop setup now refuses, because no SUCCESS_PENDING can arise there. On Revision3, both the in-frame success and the stop were accepted.
  - The fixture still issues a stop inside a CONTAINED command's cleanup frame. That is identical on both trees, pre-existing trusted-setup laxity that RemPlan-3 places out of scope.

**Enumeration diff.** My round-3 90-cell enumeration (10 command states including the two cleanup substates × 9 operations), run on both trees, differs in one cell only: `in_final_cleanup × exit_success`, which went from `accepted → success_pending` to `refused, vector unchanged`. The other 89 cells are identical.

**Stuck states.** No new stuck state: the marker is always cleared in `finally`, and the post-return success path completes exactly once. There is no NEW ARCHITECTURAL root cause.

**Effect on my round-3 retrace table.** The delta cannot affect any closure that does not call `worker_exit_success` from inside a cleanup action. All of those carry over. IR23's previously failing clause ("success exit refuses … until both steps have run") now holds. On the State side, the historical worker-exit root is no longer open through P2-1, and the failed-FIFO cleanup-failure cause can no longer be converted into a success settlement.

## Evidence base

**Tuple** (START 2026-10-04T23:57Z, END 2026-10-05T00:01Z UTC; identical both times):

| Check | Expected | START | END |
|---|---|---:|---:|
| `shasum -a 256` MANIFEST-4 | `596c8ab8…6339` | exact | exact |
| `shasum -a 256 -c` MANIFEST-4 | 156 OK | 156 OK | 156 OK |
| ReadOnly / RemInputs-3 | 741 / 13 | OK | OK |
| MANIFEST-3 inside `Revision3/garns` | 141 OK (self-hash `9a9f8b2a…`) | 141 OK | 141 OK |
| `.pyc` / `.pyo` / `__pycache__` | 0 | 0 | 0 |

MANIFEST-3 was not checked against live source. I verified the input hashes: RemPlan-3 `7c21b5d5…eda7b`, DRAFT-4 `cbd17c1b…8348`, Verification-4 `a312ebd1…8c33`, BuilderPrompt-4 `139de0db…ed56`, VerificationLogs-4 `9a194873…e295` and my prior report `9a9637bc…25c2`.

**Read:** the re-verdict prompt, RemPlan-3, DRAFT-4, BuilderPrompt-4, Verification-4, the result lines of VerificationLogs-4, the three diffs, and the new test class. Not read: the other axis's re-verdict (none existed at END), any reviewer message, any peer prompt.

**Gates** (`PYTHONDONTWRITEBYTECODE=1`, the prescribed `PYTHONPATH`, `-B`, no warning filter):

| CPython | Focused | Full (ResourceWarning lines) | Product | New class |
|---|---|---|---|---|
| 3.11.14 | Ran 190 OK | Ran 293 OK (0) | 5 PASS | Ran 3 OK |
| 3.14.3 | Ran 190 OK | Ran 293 OK (140, visible) | 5 PASS | Ran 3 OK |

**Inline probes** (stdin, read-only):
- the 8-variant P2-1 reproduction on MANIFEST-4 (3.14.3 and 3.11.14) and on Revision3;
- the late-return and stop-fixture probe on both trees;
- the 90-cell enumeration on both trees.

Private fields were read only. Nothing was written. One probe first failed with a `SyntaxError` because zsh's `echo` expanded `\n` inside the script; it was re-run unchanged via `printf '%s\n'`. No helpers, Git/GWZ, network, `tools/check.py`, `compileall` or `py_compile`.

## Findings

None at P0–P3. My P3-1 and P3-2 carry over unchanged, as tabled.

## Risks and next action

Below the bar:
- The implementation record still says "no further correction is allowed after correction 2", which is stale after the operator's exception; Verification-4 records the wording items for W3. Its IR23 row and A16's claim that a cleanup failure preserves one primary exit are accurate again on MANIFEST-4.
- The in-frame stop-fixture laxity for CONTAINED cleanup frames is pre-existing and out of scope.
- IR20, IR27 and IR28, the below-bar items from round 3, and the operator question on `CURRENT × NONE → RETIRED` are unchanged.
- This is deterministic single-process reference evidence only.

**Next action:** the lane owner files this GO as the State verdict of record for MANIFEST-4 and merges it with the Code axis's re-verdict on the same tuple. GO/GO accepts internal contracts and reference tests only, with IR20, IR27, IR28 and IR32–IR34 carried to W3.
