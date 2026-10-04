# W1A11-WorkerExitImplementation — builder prompt 2 (correction 1 of 2)

You are the sole builder for consolidated source correction 1 of the Garns v9-6
W1A11 worker-exit implementation. You write one patch, alone. Then you stop
writing and return complete testimony. You do not review, accept or close
anything: closure belongs to the reviewers who raised each finding.

PRODUCT ROOT
`/Volumes/projects/limbo/garns-wz/garns`. It is GWZ member `garns` of workspace
`/Volumes/projects/limbo/garns-wz`. Run every command from the product root.

AUTHORITY
- Operator: correction 1 was authorized on 2026-10-05.
- Controlling disposition:
  `dev-docs/W1A11-WorkerExitImplementation-RemPlan.md`.
- Write and verification rules: the execution brief, as narrowed below.
- Behavior: the accepted design. Where text conflicts, the accepted design and
  its accepted W2 composition win. Do not change accepted design, architecture,
  ownership or compatibility. If a correction would need any of those, stop
  and report it instead of improvising.

READ FULLY BEFORE WRITING, in this order:
1. `../AGENTS_GWZ.md` and the product `AGENTS.md`.
2. `dev-docs/W1A11-WorkerExitImplementation-RemPlan.md`, all of it. It maps 44
   findings to roots: IR1–IR13 (blocking), IR14–IR19 (non-blocking) and IR20
   (out of scope).
3. `dev-docs/W1A11-WorkerExitImplementation-ExecutionBrief.md`.
4. The accepted design and its accepted inputs:
   - `dev-docs/W1A11-WorkerExitRedesign.md` and
     `dev-docs/W1A11-WorkerExitRedesign-ACCEPTANCE.md`;
   - the accepted overlay `dev-docs/W2-AdmissionLifetimeRedesign.md` and
     `dev-docs/W2-AdmissionLifetimeRedesign-ACCEPTANCE.md`;
   - `docs/adr/A16-admission-lifetime.md`.
5. The four round-1 reports. Their reproductions are the counterexamples your
   tests must re-run:
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewCode-1.md`
   - `dev-docs/W1A11-WorkerExitImplementation-ReviewState-1.md`
   - `dev-docs/W1A11-WorkerExitImplementation-OriginCodeClosure-1.md`
   - `dev-docs/W1A11-WorkerExitImplementation-OriginStateClosure-1.md`
6. `dev-docs/W1A11-WorkerExitImplementation.md`, the implementation record.
   You maintain it.
7. `dev-docs/W1A11-WorkerExitImplementation-DRAFT.md`, the round-0 builder
   testimony.
8. Every source and test file in the write allowlist.

WRITE ALLOWLIST — exactly these 23 paths and nothing else:
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

The brief's narrow-purpose notes for `authority.py`, `consumers.py`,
`__init__.py`, `test_contracts.py` and the ADR README still apply.

Everything else is read-only. That includes:
- every path in the ReadOnly-741 guard, among them
  `src/garns/backends/contracts/semantic.py` and `tools/check.py`;
- every other `dev-docs/` file: reports, manifests, maps, prompts, the
  RemPlan, the checkpoint and the handoff;
- the `W1A11-WorkerExitImplementation-Baseline/` and
  `W1A11-WorkerExitImplementation-Revision1/` archives;
- the grammar, compiler, shipped runtime, evidence, package metadata and
  dependency files.

Do not create any other file.

TOOLS AND ENVIRONMENT
- Edit only with the Edit and Write tools, and only on allowlisted paths. The
  brief's `apply_patch` rule maps to these tools here; preserve unrelated
  content. Never write into the tree with shell redirection, `sed -i`, scripts
  or any other command.
- No Git or GWZ commands of any kind, including read-only ones. No network,
  installation, services or helper subagents.
- Run Python only in this form, from the product root:

  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <interpreter> -B …`

  The interpreters are:
  - `/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11`
  - `/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`
  - `/opt/homebrew/bin/python3.13`
  - `/opt/homebrew/bin/python3.14`
- Never run `tools/check.py`; it writes gate evidence. Do not use `compileall`
  or `py_compile`; use `ast.parse` for syntax checks. Add no warning filters,
  and keep the inherited SQLite `ResourceWarning`s visible.
- Scratch files go in your session scratchpad only, never in the product tree.

GUARDS — run at START, before any write, and at END, after your last write:
- `shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`
  must print `7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544`.
  The manifest file itself never changes.
- `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`
  - At START it must give 117 OK.
  - At END, list exactly which entries fail. Every failing entry must be an
    allowlisted path you changed.
- `shasum -a 256 -c` on each map below must give the stated count, START and
  END:
  - `dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256`: 31
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256`: 20
  - `dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256`: 741
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-WorkerExitRedesign-MANIFEST-3.sha256`: 115
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-MANIFEST-3.sha256`: 71
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ReadOnly.sha256`: 111
  - `dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ProductGuard.sha256`: 614
  - `dev-docs/W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256`: 13
  - `dev-docs/W1A11-WorkerExitImplementation-RemInputs.sha256`: 18
- From inside `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns`, run
  `shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256`.
  It must give 117 OK at START and END.
- There must be no `.pyc`, `.pyo` or `__pycache__` anywhere under the product
  root, at START and END.
- On any unexplained mismatch outside the allowlist, stop and report.

WHAT TO BUILD
- **Blocking roots.** Resolve IR1–IR13 exactly as the RemPlan specifies. Each
  correction carries out clauses the accepted design already states. Use the
  RemPlan's seven shared mechanisms to keep the patch cohesive:
  1. one publication precondition;
  2. one containment routine;
  3. validate-before-mutate checks on worker entries;
  4. refresh disposition routing;
  5. registry-witnessed leave;
  6. a complete coordinator protocol;
  7. bounded retention with indexed lookups.
- **Non-blocking roots.**
  - IR16 (enumeration and property tests; terminalizer and worker-entry source
    rules) is required in this correction.
  - IR14, IR15, IR17, IR18 and IR19 are recommended where they sit on paths you
    rewrite. Report each one as done or left open.
  - IR20 (G10) is out of scope. Do not touch `semantic.py` or `tools/check.py`.
- **Command slots.** Design §3 makes every command slot required, so
  publication with no dispatched command must refuse. Retained fixtures and
  helpers that publish without a command must be adapted to drive the default
  command. Retained coverage is adapted, never deleted. Do not weaken a
  retained assertion to make a test pass. If a retained test encodes behavior
  the accepted design forbids, adapt it to the design and list the change.
- **IR13 scope** is the design's stated bounds:
  - discard the command ledger and its per-command records at terminalization;
  - no evicted neutral candidate or receipt identity survives outside the
    replay ring;
  - neutral-lineage and lookup work is not proportional to lifetime history.
  Do not invent a configurable history limit.
- **Ownership.** `lifetime_reference.py` stays the sole mutable lease and worker
  owner; buffer state stays its subledger; the coordinator stays the
  deployment domain. Add no second owner, new subsystem or public surface. The
  1,780-line cohesion exception covers justified growth. Record the new size
  and the cohesion reasoning in the implementation record, and do not split
  files by line count.
- **Names** stay internal and provisional; W3 Surface freezes them later.
- **Documentation.** Update the implementation record so it describes the
  corrected bytes truthfully: method and type inventory, supersession map,
  test mapping and limits. Update A16's candidate wording wherever a claim
  changes.

TESTS
- Add the RemPlan closure tests for every root you resolve.
- Every reproduction in the four round-1 reports that demonstrates a P2, or a
  P3 you fix, must exist as a regression test. Each one runs real reference
  transitions with the repository's fixtures.
- Every refusal asserts the full unchanged-state vector the brief requires.
- **Failing-before evidence.** Run the new and changed behavioral test modules
  against the archived MANIFEST-1 sources, by putting
  `dev-docs/W1A11-WorkerExitImplementation-Revision1/garns/src` in place of
  `src` on `PYTHONPATH` (still with `-B`). Every blocking root needs at least
  one test that fails there and passes on your tree. Report the per-root
  result. Source-text rules are exempt, because they read live files.

VERIFICATION — record exact commands and outputs
- For each of the four interpreters:
  - `-B -m unittest discover -s tests/contracts -t .`
  - `-B -m unittest discover -s tests -t .`
  - `-B tools/check_product.py`
- `ast.parse` every changed or new `.py` file.
- Run all guards at END.

STOP WRITES
After verification, make no further writes. Your final message must be your
complete testimony and nothing else. The manager files it verbatim as
`dev-docs/W1A11-WorkerExitImplementation-DRAFT-2.md`. Use this format:

# W1A11-WorkerExitImplementation — DRAFT 2 (correction 1 builder testimony)

Header:
- date;
- your model;
- the object, MANIFEST-1 `7e80ca67…`;
- a statement that STOP-WRITES is in effect and nothing is self-accepted or
  claimed closed.

## Changed paths
Each path with its SHA-256 before (from MANIFEST-1, or "new") and after, and
its line count before and after.

## Root-by-root implementation
For each of IR1–IR19:
- what changed, with file and line ranges;
- which accepted-design clause it carries out;
- which tests cover each mapped reviewer counterexample;
- its status: implemented, or left open with the reason.

IR20: untouched.

## Retained-test adaptations
Every changed retained test or fixture, and why.

## Failing-before evidence
Per blocking root: the test and its result on the Revision1 sources and on
yours.

## Test inventory and counts
The new tests, and the focused and full totals before and after.

## Verification
- exact commands and outputs for each interpreter;
- guard results at START and END;
- the MANIFEST-1 live entries that fail, all of which must be allowlisted paths
  you changed.

## Limits and open items
Anything not done, any doubt, and anything that may need operator direction.
