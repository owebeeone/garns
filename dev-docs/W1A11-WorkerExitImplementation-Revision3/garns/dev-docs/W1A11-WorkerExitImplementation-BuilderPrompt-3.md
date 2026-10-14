# W1A11-WorkerExitImplementation — builder prompt 3 (correction 2 of 2, the last)

You are the same builder that wrote correction 1, and your context is intact.
You now write consolidated source correction 2 of 2, alone, as one patch.
Then you stop writing and return complete testimony. You do not review, accept
or close anything: closure belongs to the reviewers who raised each finding.

THIS IS THE LAST CORRECTION THE IMPLEMENTATION GATE ALLOWS. If round 3 finds
any new P0–P2, the lane stops for the operator. So:
- Make surgical changes that resolve exactly the listed roots.
- Do not refactor, rename or restructure anything else.
- Change no behavior outside the listed roots.
- Keep every correction-1 behavior that round 2 confirmed.

PRODUCT ROOT
`/Volumes/projects/limbo/garns-wz/garns`. Run every command from there.

AUTHORITY
- Operator: correction 2 was authorized on 2026-10-05.
- Controlling disposition:
  `dev-docs/W1A11-WorkerExitImplementation-RemPlan-2.md`.
- Write and verification rules: the execution brief, as narrowed below.
- Behavior: the accepted design and its accepted W2 composition win over any
  conflicting text.
- If a root cannot be resolved without an accepted-design, architecture,
  ownership or compatibility change, STOP and report it. Do not improvise.

READ FULLY BEFORE WRITING
1. `dev-docs/W1A11-WorkerExitImplementation-RemPlan-2.md`, all of it:
   - IR21–IR23 are blocking.
   - IR24, IR25, IR26, IR29 and IR30 are to be fixed now.
   - IR27 and IR28 are deferred to W3; do not implement them.
   - IR20 is out of scope.
2. The six round-2 reports. Their reproductions are the counterexamples your
   tests must re-run:
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-2.md`
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewState-2.md`
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-1-Reverdict.md`
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewState-1-Reverdict.md`
   - `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1-Reverdict.md`
   - `dev-docs/W1A11-WorkerExitImplementation-OriginStateClosure-1-Reverdict.md`
3. `dev-docs/W1A11-WorkerExitImplementation-Verification-2.md`. Read its
   failing-before classification closely: 10 tests failed on the archive only
   because an API was missing, and IR12 had no behavioral failing-before test.
4. The accepted design §§4–9 again, where IR21–IR23 cite them:
   `dev-docs/W1A11-WorkerExitRedesign.md`, plus the overlay
   `dev-docs/W2-AdmissionLifetimeRedesign.md` §4 and §6.
5. The current allowlisted sources and tests, as you left them.

WRITE ALLOWLIST — unchanged: the same 23 paths as BuilderPrompt-2.
- `src/garns/backends/contracts/`: `admission.py`, `authority.py`,
  `consumers.py`, `worker_authority.py`, `lifetime_reference.py`,
  `buffer_reference.py`, `snapshot_reference.py`, `generation_reference.py`,
  `migration_reference.py`, `lifetime.py`, `protocols.py`, `values.py`,
  `__init__.py`
- `tests/contracts/`: `test_admission_contracts.py`,
  `test_lifetime_contracts.py`, `test_worker_authority.py`,
  `test_generation_contracts.py`, `test_contracts.py`,
  `test_worker_exit_contracts.py`, `test_contract_source_rules.py`
- `docs/adr/A16-admission-lifetime.md`
- `docs/adr/README.md`: candidate status and history links only
- `dev-docs/W1A11-WorkerExitImplementation.md`

Everything else is read-only. That includes:
- every ReadOnly-741 path;
- every other `dev-docs/` file;
- the Baseline, Revision1 and Revision2 archives.

Create no other file.

TOOLS AND ENVIRONMENT — unchanged from BuilderPrompt-2:
- Use the Edit and Write tools, on allowlisted paths only.
- No Git or GWZ commands, network, installation, services or helpers.
- Run Python as
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <interpreter> -B …`
  on the four interpreters.
- Never run `tools/check.py`, `compileall` or `py_compile`.
- Add no warning filters.
- Scratch files go in your session scratchpad only.

GUARDS — run at START, before any write, and at END, after your last write:
- `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256`
  must print `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720`.
- `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256`
  - At START it must give 128 OK.
  - At END, list exactly which entries fail. Each must be an allowlisted path
    you changed in this correction.
- `shasum -a 256 -c` on each map below must give the stated count, START and
  END:
  - `dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256`: 31
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256`: 20
  - `dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256`: 741
  - the four Legacy maps inside the Baseline directory: 115, 71, 111, 614
  - `dev-docs/W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256`: 13
  - `dev-docs/W1A11-WorkerExitImplementation-RemInputs.sha256`: 18
  - `dev-docs/W1A11-WorkerExitImplementation-RemInputs-2.sha256`: 22
- From inside `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns`,
  `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`
  must give 117 OK.
- From inside `dev-docs/W1A11-WorkerExitImplementation-Revision2/garns`,
  `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256`
  must give 128 OK.
- Do not check MANIFEST-1 against live source.
- There must be no `.pyc`, `.pyo` or `__pycache__` anywhere under the product
  root.
- On any unexplained mismatch outside the allowlist, stop and report.

WHAT TO BUILD — exactly as RemPlan-2 specifies

- **IR21.**
  - `open_lifetime` refuses once the registry's runtime resource has left
    `LOCAL_OPEN`, or once a runtime close has begun. A registry that was never
    joined and whose close has begun proceeds only `UNJOINED → LEFT` through
    `close_unjoined`.
  - `close_outcome` establishes every coordinator precondition before its first
    local mutation. A refusal leaves resources, admissions and membership
    unchanged.
  - `_admit` refuses when the runtime is not `LOCAL_OPEN`.
  - A repeated `start_close` never relabels RETIRED or REVOKED admissions.
- **IR22.**
  - Preferred: remove `revoke` from the executor façade, together with the
    uncalled `_revoke_worker_authorization`. If you keep a route instead, it
    must validate the exact assigned worker or the live receiver through the
    trusted providers before any mutation.
  - Add a source rule that enumerates every public method reaching
    `_contain_lease` and requires each to validate a receiver, an assigned
    worker, or a trusted observation or barrier first.
  - Adapt any retained test that used the façade `revoke` so its attack is
    kept, not deleted.
- **IR23.**
  - Claim the cleanup step atomically with its validation, before invoking the
    action. A claimed step counts as consumed whether the action returns or
    raises.
  - Refuse any cleanup call while that command's cleanup action is on its
    stack.
  - Refuse effect reservation once cleanup has begun.
- **IR24.** Clear `active_command_serial` when terminal history is discarded.
  A late delivery-stop setup on a terminal retirement refuses or replays; it
  never raises `IndexError`.
- **IR25.** Validate the exact current assigned worker before recording the
  late-return diagnostic.
- **IR26.** Discard an operation's unconsumed initial-snapshot candidate when
  the operation becomes terminal.
- **IR29.** Declare `recover_migration` in the formal
  `SharedGenerationCoordinator` seam and in the source rule's member set.
- **IR30.** Add a test that drives issuing-task `run_effect` after a distinct
  worker has dequeued. Callers: the receiver, a third task and the worker.
- **Leave alone.** Do NOT implement IR27 or IR28. Do NOT touch `semantic.py`
  or `tools/check.py`.
- **Ownership.** `lifetime_reference.py` stays the sole mutable owner.
- **Documentation.** Update the implementation record and A16 wherever a claim
  changes. Record each round-2 finding you resolve.

TESTS
- Add the RemPlan-2 closure tests for every root you resolve.
- Every round-2 reproduction of a P2, and of each P3 you fix, must exist as a
  regression test that runs real reference transitions.
- Every refusal asserts the full unchanged-state vector the brief requires.
- **Failing-before evidence.**
  - Run the new and changed behavioral test modules against the archived
    MANIFEST-2 sources in `dev-docs/W1A11-WorkerExitImplementation-Revision2/garns/src`.
    Use your correction-1 method: copy the modules into a scratchpad package
    with empty `__init__.py` files, because `tests/__init__.py` forces the
    live `src`.
  - Classify each failure there as behavioral or API-absence.
  - Every blocking root (IR21, IR22, IR23) needs at least one test that fails
    behaviorally on Revision2 and passes on your tree. Write such tests with
    observers that already exist on MANIFEST-2.
  - Report the result per root.
- Retained coverage is adapted, never deleted.

VERIFICATION — record exact commands and outputs
- For each of the four interpreters:
  - focused: `-B -m unittest discover -s tests/contracts -t .`
  - full: `-B -m unittest discover -s tests -t .`
  - product: `-B tools/check_product.py`
- `ast.parse` every changed `.py` file.
- Run all guards at END.

STOP WRITES
After verification, make no further writes. Your final message must be your
complete testimony and nothing else. The manager files it verbatim as
`dev-docs/W1A11-WorkerExitImplementation-DRAFT-3.md`. Use the DRAFT-2 format,
with these changes:
- The heading is `DRAFT 3 (correction 2 builder testimony)`.
- The object is MANIFEST-2 `ee441c18…`.
- "Changed paths" gives SHA-256 values before (from MANIFEST-2) and after.
- "Root-by-root implementation" covers IR21–IR26, IR29 and IR30, and says that
  IR27, IR28 and IR20 are untouched.
- "Failing-before evidence" classifies each failure as behavioral or
  API-absence.
- "Limits and open items" names anything that may need operator direction.
