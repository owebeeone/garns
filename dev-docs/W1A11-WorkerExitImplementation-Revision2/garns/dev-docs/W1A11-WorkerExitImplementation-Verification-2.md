# Worker exit implementation manager verification 2

Date: 2026-10-05. Owner: manager.  
Status: corrected candidate verified for review round 2. This is not accepted
source.

Correction 1 of 2 ran under the
[RemPlan](W1A11-WorkerExitImplementation-RemPlan.md) and
[BuilderPrompt-2](W1A11-WorkerExitImplementation-BuilderPrompt-2.md).

- **Builder.** One fresh Claude subagent dispatched with model parameter
  `fable`. Its transcript shows every turn on `claude-fable-5-1`, from
  2026-10-04 13:08:03Z to 14:53:54Z.
- **Testimony.** The builder declared STOP-WRITES before these checks. Its
  testimony is filed verbatim as
  [DRAFT-2](W1A11-WorkerExitImplementation-DRAFT-2.md), SHA-256
  `cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30`.
- **Scope of this record.** It closes no finding and changes neither the
  accepted design nor the older two-correction histories.

## Reproduced test matrix

| CPython | Focused contracts | Full tests | Product checks |
|---|---:|---:|---:|
| 3.11.14 | 173 passed | 276 passed | 5 passed |
| 3.12.12 | 173 passed | 276 passed | 5 passed |
| 3.13.12 | 173 passed | 276 passed | 5 passed |
| 3.14.3 | 173 passed | 276 passed | 5 passed |

All 12 commands exited zero.
[VerificationLogs-2](W1A11-WorkerExitImplementation-VerificationLogs-2.md)
holds the exact commands and complete outputs. Inherited SQLite
`ResourceWarning` lines stayed visible: 116 on 3.13 and 84 on 3.14, the same
counts the builder reported. No warning filter, dependency, service or network
access was used.

The counts match the testimony. The focused suite went from 130 to 173 tests:
40 new causal tests in `test_worker_exit_contracts.py` and 3 new source rules.
The full suite went from 233 to 276. An AST comparison found all 225 test
methods of the MANIFEST-1 test files still present; no retained test was
removed. All 27 contract and contract-test files AST-parse.

## Guards and changed paths

| Check | Result |
|---|---|
| MANIFEST-1 self-hash | `7e80ca67…ea544`, unchanged |
| MANIFEST-1 live content | 104 OK, 13 changed |
| Implementation Inputs | 31 OK |
| Implementation Baseline | 20 OK |
| Implementation ReadOnly | 741 OK |
| Legacy design / stopped source / old read-only / old product | 115 / 71 / 111 / 614 OK |
| Design AcceptanceEvidence | 13 OK |
| RemInputs | 18 OK |
| MANIFEST-1, verified from inside `W1A11-WorkerExitImplementation-Revision1/garns` | 117 OK |
| `.pyc`, `.pyo`, `__pycache__` under the product root | none |

The 13 changed MANIFEST-1 entries are exactly the 13 paths DRAFT-2 lists, and
all are inside the brief's allowlist:

- five contract modules: `lifetime_reference.py`, `generation_reference.py`,
  `lifetime.py`, `buffer_reference.py`, `snapshot_reference.py`;
- six contract test modules;
- A16;
- the implementation record.

Git shows no added or deleted file under `src/` or `tests/`. Every other
change in the tree is a manager-owned record:

- the checkpoint;
- the RemPlan status;
- BuilderPrompt-2;
- RemInputs;
- the Revision1 archive;
- DRAFT-2 and these two verification documents.

## Failing-before evidence, reproduced

The builder's PYTHONPATH method needs one adjustment. `tests/__init__.py`
inserts the live `src` at the front of `sys.path`, so swapping `PYTHONPATH`
alone still runs the corrected sources.

The manager therefore copied the six behavioral contract modules into a
scratchpad package with an empty `tests/__init__.py`. `test_contract_source_rules.py`
was copied too, only for constants the worker-exit tests import. The modules
were then run on Python 3.14 against each tree, with the Revision1 archive's
`src` in place of `src`. `garns.__file__` resolved into the archive.

| Sources | Result |
|---|---|
| Archived MANIFEST-1 (Revision1) | Ran 159; FAILED (failures=29, errors=209) |
| Corrected tree | Ran 159; OK |

This reproduces the builder's numbers. Classifying the archive run by each
failure's final exception:

- **68 distinct tests fail.**
- **58 fail on behavior:** an assertion, or a refusal where the corrected
  contract proceeds.
- **10 fail only because an API is missing in MANIFEST-1.** They hit the new
  observers `lease_facts` or `worker_cleanup_step`, or the membership-bound
  coordinator signatures, before reaching the behavior under test.

Every blocking root has at least one behaviorally failing test, with one
exception. IR12's only failing-before test
(`test_hard_fence_contains_accepted_unpublished_leases`) fails on the missing
`lease_facts` observer. That is weaker evidence for IR12 than for the other
roots. The originating Code reviewer's re-run of its own counterexample decides
IR12 closure.

Two new tests pass on both trees, as DRAFT-2 states. They are kept as
regressions.

## Limits

This is deterministic single-process reference evidence. Passing suites and
failing-before runs are not closure. Every round-1 finding stays open until the
reviewer who raised it verifies its counterexample on the corrected tuple.
Fresh full Code and State review of the whole corrected object is also
required, because the correction changes call graphs and the formal coordinator
protocol.

The implementation correction count is now 1 of 2. MANIFEST-2 pins this
record. Its own SHA-256 is recorded in the checkpoint, because a manifest
cannot appear inside a file it pins.
