# W1A11-WorkerExitImplementation — DRAFT 4 (correction 3 builder testimony)

- **Date:** 2026-10-05.
- **Model:** Claude Sonnet 5.5 (`claude-sonnet-5-5`). I am a fresh subagent dispatched with model parameter `sonnet`, with no prior context.
- **Object:** MANIFEST-3 (`dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256`, SHA-256 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9`, 141 entries). This draft reports a three-path delta against it. I produced no MANIFEST-4.
- **Brief:** `dev-docs/W1A11-WorkerExitImplementation-BuilderPrompt-4.md`, SHA-256 `139de0dbec35b6d83312bdc77b68fd60b1cc75f966006dd88e40143ca17ced56`. I verified it before any work. The operator authorized the exception on 2026-10-05.
- **STOP-WRITES is in effect.** My last write to the product tree was the implementation-record entry. It came before the verification runs and the END guards, and nothing has been written since.
- **Nothing is self-accepted.** This is builder testimony only. I did not review, accept or close IR31 or anything else.

## 1. The source line

`src/garns/backends/contracts/lifetime_reference.py`, `worker_exit_success`, line 664.

Before:

```python
        if command.next_cleanup_step <= command.spec.cleanup_steps:
```

After:

```python
        if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:
```

- Line 665 is unchanged: `raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "trusted cleanup schedule is incomplete")`.
- The file is still 2,074 lines.
- `diff` against the archived MANIFEST-3 copy prints only `664c664`.

## 2. Changed paths

| Path | SHA-256 before (equals MANIFEST-3) | SHA-256 after |
|---|---|---|
| `src/garns/backends/contracts/lifetime_reference.py` | `803a3008b52f62df926250b2f0528e7e15f186d584c4d67e4286b2d4162e4723` | `15abd5c2d53d84697233e1d439f7c1ddc99f123a7fb8900ae1cdc69f0c0bd703` |
| `tests/contracts/test_worker_exit_contracts.py` | `189982b4f40d7bfb0537e44bc6d2600baf4c118e85a18c947a3679d62691c551` | `96b062444fccc45b125ce750de238a4df7348eaec4a581191bacfafe254abf7a` |
| `dev-docs/W1A11-WorkerExitImplementation.md` | `a15a937bda3b11267e9a1bd4315d823f4e7b8a2f14f2f9570126904c6099193e` | `f8b09086045905ba2ca9390de33e7a5650e9aed4eaf24de2e76c4ad4598bbb5e` |

Delta against the archived MANIFEST-3 copies (read-only `diff`):

| Path | Delta |
|---|---|
| Source | One line changed, `664c664`. |
| Test file | 193 lines added, 0 removed or changed. The new class sits at lines 3068–3260, between `CleanupClaimTests` and `TerminalTombstoneTests`. |
| Record | 1 line added, 0 removed or changed. It is a table row, now line 158, after IR30 in "Executable regression disposition". |

A `find -newer` against my START-guard marker lists exactly these three files under the product root. Nothing under `/Volumes/projects/limbo/datascad` was written.

## 3. New tests

Class `CleanupInFlightSuccessExitTests` in `tests/contracts/test_worker_exit_contracts.py`.

Helpers (not tests):
- `hostile_cleanup` is a trusted cleanup provider. Earlier steps are inert. The final step's fixed action calls `worker_exit_success(authorization, result)` from inside its own frame. It records the refusal, or the accepted receipt, and the full `vector(...)` before and after the call. It then optionally raises `EffectFault`.
- `execute_scenario` builds EXECUTE with LOWER done, a distinct assigned worker, effect 1 returned and the private result computed.
- `assert_in_frame_refusal` runs the shared in-frame assertions below.

The in-frame outcome is recorded inside the action and asserted outside it. A failing assertion therefore cannot be swallowed by `run_worker_cleanup` as a cleanup failure.

Shared in-frame assertions, used by all three tests:
- The cleanup actions ran exactly `[1..K]`.
- The in-frame call was not accepted.
- It was refused with `RefusalCode.WORKER_AUTHORITY_INVALID`.
- The full `vector(registry, lease, authorization, coordinator=…[, registration=…])` is identical before and after the refused call.

**`test_raising_final_cleanup_after_an_in_frame_success_request_is_the_primary_failure`** (line 3146; subTests K=1 and K=2). EXECUTE; steps 1..K−1 run normally; step K requests success exit in-frame, then raises. Beyond the shared assertions:
- The primary exit is FAILURE, with an exit receipt and 0 diagnostics.
- The command is `CONTAINED`.
- The lease is `CONTAINED` with owner label `"containment"`.
- The cleanup step counter is K+1, publications are 0 and the coordinator count is 1.
- After `setup_reference_worker_stop` and `observe_worker_stopped`, `complete_contained` gives `REFUSED` with count 0 and publications 0.

**`test_returning_final_cleanup_refuses_in_frame_then_allows_exactly_one_success_exit`** (line 3177; subTests K=1 and K=2). EXECUTE; the final action refuses in-frame and returns. Beyond the shared assertions:
- After both cleanups, the step counter is K+1.
- `worker_exit_facts == (None, None, 0, False)`, so the refused request recorded nothing.
- The state is `RUNNING_IDLE` and publications are 0.
- `worker_exit_success` then returns a `WorkerExitReceipt`.
- A second identical call returns the identical receipt, so there is exactly one receipt.
- The facts are `(SUCCESS, receipt, 0, False)`.
- After the worker stop, `accept_worker_result` returns `"private-value"`.
- The PUBLICATION plan step gives publications 1, lease `SUCCEEDED` and count 0.

**`test_iterator_handoff_head_with_a_failing_final_cleanup_retires_instead_of_settling_delivered`** (line 3207; K=1, raising). Two queued ranges via `two_range_handoff`. Before the cleanup, the cursors are (2, 0) and the count is 2. Beyond the shared assertions, with `registration=` in the vector:
- The primary exit is FAILURE with 0 diagnostics.
- The command is `CONTAINED` and the lease is `RETIRING_HANDOFF`.
- The count is 1, so the successor permit was released once.
- The cursors stay (2, 0).
- Publications equal the baseline.
- `dequeue_buffer` of the successor raises `ContractRefusal`.
- `settle_retirement` (exact worker stop, delivery stop, `settle_delivery_non_success`) returns `RefetchRequired`.
- After that, the count is 0, the delivered cursor revision is 0, the lease is `REFUSED` and publications are at the baseline.

## 4. Failing-before on Revision3, passing on the corrected tree

**Method.**
- The scratchpad package copy has empty `tests/__init__.py` and `tests/contracts/__init__.py`, plus all eight `tests/contracts/test_*.py` files.
- I copied those files after my test edit, so the copy contains the new class.
- Run from inside the copy with `PYTHONPATH=/Volumes/projects/limbo/garns-wz/garns/dev-docs/W1A11-WorkerExitImplementation-Revision3/garns/src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`.
- `PYTHONDONTWRITEBYTECODE=1 … python -B -m unittest -v tests.contracts.test_worker_exit_contracts.CleanupInFlightSuccessExitTests`.
- I checked import resolution: `lifetime_reference.__file__` resolved under Revision3 and the test module resolved to the scratch copy.
- The archived `lifetime_reference.py` has SHA-256 `803a3008…`, the same as the pre-fix live file.

| Test | Revision3, 3.11.14 and 3.14.3 | Corrected tree, 3.11.14 and 3.14.3 |
|---|---|---|
| Handoff, K=1, raising | FAIL | ok |
| EXECUTE raising, K=1 | FAIL | ok |
| EXECUTE raising, K=2 | FAIL | ok |
| EXECUTE returning, K=1 | FAIL | ok |
| EXECUTE returning, K=2 | FAIL | ok |

- **Revision3:** both interpreters print `Ran 3 tests in 0.002s` / `FAILED (failures=5)`. All five fail in `assert_in_frame_refusal` with `AssertionError: WorkerExitReceipt(<opaque identity>) is not None : success exit was accepted from inside the final cleanup action`. This is the IR31 behavior.
- **Corrected tree:** both interpreters print `Ran 3 tests in 0.001s` / `OK`.

## 5. Verification

Every command ran from `/Volumes/projects/limbo/garns-wz/garns` as `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <python> -B …`.

| Interpreter | `-m unittest discover -s tests/contracts -t .` | `-m unittest discover -s tests -t .` | `tools/check_product.py` |
|---|---|---|---|
| 3.11.14 (`/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11`) | exit 0, `Ran 190 tests in 0.259s`, `OK` | exit 0, `Ran 293 tests in 1.725s`, `OK` | exit 0 |
| 3.14.3 (`/opt/homebrew/bin/python3.14`) | exit 0, `Ran 190 tests in 0.308s`, `OK` | exit 0, `Ran 293 tests in 1.660s`, `OK` | exit 0 |

- The 190 contracts tests include the 3 new test methods.
- `check_product.py` printed the same five lines on both interpreters: `PASS product paths`, `PASS pinned baseline inputs`, `PASS cache hygiene`, `PASS shipped path hygiene`, `PASS W0 product baseline`.

## 6. Guards

| Guard | START (before any write) | END (after last write) |
|---|---|---|
| `BuilderPrompt-4.md` SHA-256 | `139de0db…ced56`, match | not re-run |
| `RemInputs-3.sha256` file SHA-256 | `f0fd698a…a155`, match | not re-run |
| `MANIFEST-3.sha256` file SHA-256 | `9a9f8b2a…6af9`, match | `9a9f8b2a…6af9`, match |
| `shasum -a 256 -c` MANIFEST-3 | 141 OK, 0 failed | 138 OK; exactly 3 FAILED: `dev-docs/W1A11-WorkerExitImplementation.md`, `src/garns/backends/contracts/lifetime_reference.py`, `tests/contracts/test_worker_exit_contracts.py` |
| `ReadOnly.sha256` | 741 entries, 741 OK | 741 OK, 0 non-OK |
| `RemInputs-3.sha256` | 13 entries, 13 OK | 13 OK, 0 non-OK |
| Revision3 inner `shasum -a 256 -c dev-docs/…MANIFEST-3.sha256` | 141 OK | 141 OK |
| `.pyc` / `.pyo` / `__pycache__` under product root | 0 | 0 |

## 7. Limits

- **Scope.** I changed one source line and nothing else. IR32–IR34, IR27, IR28, the stop fixture that ignores an active cleanup frame, and `worker_exit_failure` called inside a cleanup action are untouched and untested.
- **"Before every mutation".** The new gate precedes every mutation on the path that creates the success receipt.
  - In the same function, the earlier already-committed branch (`exit_receipt is not None`) is evaluated before the gate.
  - That branch has its own existing write, `late_return_diagnostic = True` at line 658.
  - It always raises or returns, and it is reachable from inside a cleanup action only after an exit receipt already exists, which is not the IR31 sequence.
  - I did not change or test it. ReviewCode-3 P2-1's wording "including the late-return diagnostic path" is therefore not exercised by my tests.
- **Failing-before depth.** On Revision3 every new test stops at the first behavioral assertion, the in-frame acceptance. The later assertions were not reached there. The downstream pre-fix values (primary success, diagnostic 1, `SUCCEEDED`, delivered cursor 1) come from the reviewers' reproductions, which I did not re-run to that depth.
- **Test breadth.**
  - The brief fixed K for the raising EXECUTE test (K=1 and K=2) and the handoff test (K=1, raising).
  - I also ran the returning EXECUTE test for K=1 and K=2, because the brief did not restrict K.
  - There is no handoff test for K=2 or for a returning action.
- **Record.**
  - I added one table row (line 158) and did not edit existing text.
  - The IR23 row (line 152, "success exit and publication wait for both steps") is unchanged.
  - The sentence "no further correction is allowed after correction 2" and the "Round-3 … remain mandatory" sentence are unchanged.
  - DRAFT-3 is untouched.
  - ReviewCode-3 P2-1 asked for these wording corrections. The one-entry allowlist did not permit them, so they are for the manager or operator.
- **Interpreters.** I ran only 3.11.14 and 3.14.3. The manager reproduces all four.
- **Evidence kind.** This is single-process reference evidence, per the record's own limits.
- **Reads beyond the listed set.** I read these to write real-transition tests and place the record row:
  - the workspace `AGENTS_GWZ.md`, which the workspace `AGENTS.md` directs; it changed nothing;
  - existing handoff and cleanup tests in the test file, and the helpers `build_fixture`, `run_command`, `make_lifetime_fixture`, `register`, `publish` and `step`;
  - `lifetime_reference.py` lines 786–960 and 1818–1975, and `ContractRefusal` in `values.py`;
  - record lines 118–262.
- **Conduct.** I used no Git or GWZ command, no network, no installation and no helper. I did not run `tools/check.py`, `compileall` or `py_compile`. Product-tree edits were made only with the Edit tool.
- **Scratch.** Scratch artifacts are in `/private/tmp/claude-501/-Volumes-projects-limbo-garns-wz/991aef8c-f901-4683-99de-a346ccb2b891/scratchpad/`, outside the product root. They are the `rev3run/` copy, the logs and the before/after hash lists, and they may not persist after the session.
