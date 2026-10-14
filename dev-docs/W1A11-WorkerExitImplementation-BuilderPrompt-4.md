# W1A11-WorkerExitImplementation — builder prompt 4 (correction 3: one-line regression fix)

You are a fresh builder for one narrowly scoped source correction. After the
two-correction gate was exhausted, the operator authorized it as an exception.
It is exactly ONE changed source line, plus regression tests and one record
entry. You write it alone, then stop writing and return testimony. You do not
review, accept or close anything.

PRODUCT ROOT: `/Volumes/projects/limbo/garns-wz/garns`. Run every command from
there.

THE DEFECT (RemPlan-3 IR31; found independently by several round-3 reviewers)
- Correction 2 made `run_worker_cleanup` claim the cleanup step before running
  the cleanup action: `next_cleanup_step += 1` and `cleanup_in_progress = True`
  (`src/garns/backends/contracts/lifetime_reference.py`, about lines 697–748).
- `worker_exit_success` (about lines 642–677) still gates only on
  `if command.next_cleanup_step <= command.spec.cleanup_steps:` (about line 664).
- So a success exit requested from inside the LAST cleanup action is accepted.
- If that action then raises, the failure is only a diagnostic and the operation
  publishes SUCCEEDED. On an iterator handoff, the failed head settles as
  delivered.
- Design §5.1 and §5.3 require success exit only after every cleanup step has
  returned. A cleanup failure with no earlier primary is the primary FAILURE.

THE FIX — exactly one changed line
In `worker_exit_success`, change the cleanup gate so it also refuses while a
cleanup action is in progress:

    if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:

- Keep the existing
  `raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "trusted cleanup schedule is incomplete")`
  on the next line unchanged.
- This check comes before every mutation in that function.
- Change no other source line anywhere.

WRITE ALLOWLIST — exactly these three paths, nothing else:
- `src/garns/backends/contracts/lifetime_reference.py`: that one line only.
- `tests/contracts/test_worker_exit_contracts.py`: add new test methods (a new
  test class is fine). Do not modify existing tests.
- `dev-docs/W1A11-WorkerExitImplementation.md`: one short entry recording IR31
  and its tests.

Everything else is read-only. Use the Edit tool only; never write into the tree
from the shell.

READ ONLY WHAT YOU NEED
- `dev-docs/W1A11-WorkerExitImplementation-RemPlan-3.md`: the IR31 disposition
  and closure test.
- The "[P2-1]" section of
  `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-3.md`: the reproduction
  and closure test.
- The "[P2-9]" section of
  `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1-Reverdict-2.md`:
  the iterator-handoff variant.
- `lifetime_reference.py` lines 600–760.
- In `tests/contracts/test_worker_exit_contracts.py`: the imports and fixtures
  at the top, and class `CleanupClaimTests` (about lines 2942–3066). Reuse its
  fixture pattern and the `vector` helper.

TESTS TO ADD
Use real transitions with the repository fixtures, and assert the full
`vector(...)` unchanged on every refusal.
1. **EXECUTE, raising action, `cleanup_steps` K=1 and K=2.**
   - The final step's fixed hostile cleanup action calls
     `worker_exit_success(authorization, result)`. It is refused
     (`WORKER_AUTHORITY_INVALID`) with the vector unchanged.
   - When the action then raises:
     - the primary exit is FAILURE;
     - the command is CONTAINED under the containment owner;
     - publications stay 0;
     - after the worker stop, `complete_contained` gives REFUSED with count 0.
2. **EXECUTE, non-raising action.** The in-frame request refuses. After the
   action returns, `worker_exit_success` succeeds exactly once and the operation
   publishes once.
3. **ITERATOR_HANDOFF with two queued ranges, K=1, raising variant.**
   - The in-frame success is refused.
   - The handoff reaches RETIRING_HANDOFF, with the successor released once.
   - Cursors stay (2, 0), and the successor dequeue refuses.
   - After the stops, `settle_delivery_non_success` returns `RefetchRequired`
     with count 0.

FAILING-BEFORE
Run your new test class against the archived MANIFEST-3 sources in
`dev-docs/W1A11-WorkerExitImplementation-Revision3/garns/src`.
- Use a scratchpad package copy of `tests/contracts` with empty `__init__.py`
  files, because `tests/__init__.py` forces the live `src`.
- The new tests must fail there behaviorally and pass on the corrected tree.

GUARDS — run at START, before any write, and at END, after your last write
- `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256`
  must print `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9`.
- `shasum -a 256 -c` on that manifest must give 141 OK at START. At END exactly
  the 3 allowlisted paths fail.
- `shasum -a 256 -c` on each map must give all OK at START and END:
  - `dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256` (741 entries)
  - `dev-docs/W1A11-WorkerExitImplementation-RemInputs-3.sha256` (13 entries)
- From inside `dev-docs/W1A11-WorkerExitImplementation-Revision3/garns`,
  `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256`
  must give 141 OK.
- There must be no `.pyc`, `.pyo` or `__pycache__` anywhere under the product
  root.

ENVIRONMENT
- Run Python only as
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <python> -B …`.
- No Git or GWZ commands, network, installation or helpers.
- Do not run `tools/check.py`, `compileall` or `py_compile`.
- Scratch files go in your session scratchpad only.

VERIFICATION
On `/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11`
and `/opt/homebrew/bin/python3.14`, run:
- `-B -m unittest discover -s tests/contracts -t .`
- `-B -m unittest discover -s tests -t .`
- `-B tools/check_product.py`

The manager reproduces all four interpreters.

STOP WRITES
After verification, make no further writes. Your final message must be your
testimony only. The manager files it verbatim as
`dev-docs/W1A11-WorkerExitImplementation-DRAFT-4.md`. Use this format:

# W1A11-WorkerExitImplementation — DRAFT 4 (correction 3 builder testimony)

- Header: date, your model, the object (MANIFEST-3), a statement that
  STOP-WRITES is in effect, and a statement that nothing is self-accepted.
- The exact source line before and after, with its line number.
- The changed paths, each with SHA-256 before and after.
- The new tests, by name, and what each asserts.
- Failing-before results on Revision3 and passing results on the corrected
  tree.
- Verification commands and outputs.
- Guard results at START and END.
- Limits.
