# Worker exit implementation manager verification 3

Date: 2026-10-05. Owner: manager.  
Status: corrected candidate after correction 2 of 2 (the last), verified for review
round 3. It is not accepted source.

Correction 2 ran under [RemPlan-2](W1A11-WorkerExitImplementation-RemPlan-2.md) and
[BuilderPrompt-3](W1A11-WorkerExitImplementation-BuilderPrompt-3.md).

- **Builder.** The same builder that wrote correction 1 was resumed with its context
  intact. Its resumed transcript shows every turn on `claude-fable-5-1`, from
  2026-10-04 22:43:13Z to 22:59:59Z.
- **Testimony.** It declared STOP-WRITES before these checks. Its testimony is filed
  verbatim as [DRAFT-3](W1A11-WorkerExitImplementation-DRAFT-3.md), SHA-256
  `62e2ec64f13b4aa9d9c878f097643ceb507e1dc8a66481aa102f559be13dede7`.
- **What this record does not do.** It closes no finding and changes neither the
  accepted design nor any earlier record.

## Reproduced test matrix

| CPython | Focused contracts | Full tests | Product checks |
|---|---:|---:|---:|
| 3.11.14 | 187 passed | 290 passed | 5 passed |
| 3.12.12 | 187 passed | 290 passed | 5 passed |
| 3.13.12 | 187 passed | 290 passed | 5 passed |
| 3.14.3 | 187 passed | 290 passed | 5 passed |

- **Logs.** All 12 commands exited zero. Exact commands and complete outputs are in
  [VerificationLogs-3](W1A11-WorkerExitImplementation-VerificationLogs-3.md).
- **Warnings.** The inherited SQLite `ResourceWarning` lines stayed visible: 114 on
  3.13 and 140 on 3.14. The builder reported 112 and 140. These counts depend on
  garbage-collection timing; no warning filter was applied.
- **Counts.** They match the testimony. The focused suite went from 173 to 187, with
  13 new worker-exit tests and 1 new source rule. The full suite went from 276 to
  290.
- **No test lost.** An AST comparison found all 268 test methods of the MANIFEST-2
  test files still present, plus 14 new ones. All 27 contract and contract-test
  files AST-parse.

## Guards and changed paths

| Check | Result |
|---|---|
| MANIFEST-2 self-hash | `ee441c18…200720`, unchanged |
| MANIFEST-2 live content | 120 OK, 8 changed |
| Implementation Inputs / Baseline / ReadOnly | 31 / 20 / 741 OK |
| Legacy design / stopped source / old read-only / old product | 115 / 71 / 111 / 614 OK |
| Design AcceptanceEvidence | 13 OK |
| RemInputs / RemInputs-2 | 18 / 22 OK |
| MANIFEST-1 from inside `Revision1/garns` | 117 OK |
| MANIFEST-2 from inside `Revision2/garns` | 128 OK |
| `.pyc`, `.pyo`, `__pycache__` under the product root | none |

The 8 changed MANIFEST-2 entries are exactly the 8 paths in DRAFT-3, all inside the
brief's allowlist:
- `lifetime_reference.py`
- `worker_authority.py`
- `snapshot_reference.py`
- `lifetime.py`
- the two new-in-this-lane test modules
- A16
- the implementation record

Git shows no added or deleted file under `src/` or `tests/`. Every other change in
the tree is a manager record:
- the checkpoint
- the RemPlan-2 status
- BuilderPrompt-3
- RemInputs-2
- the Revision2 archive
- DRAFT-3 and these two verification documents

## Failing-before evidence, reproduced

Method:
- The six behavioral contract modules were copied into a scratchpad package with an
  empty `tests/__init__.py`, because the live `tests/__init__.py` forces the live
  `src`.
- `test_contract_source_rules.py` was copied too, only for the constants the tests
  import.
- The package was run on Python 3.14 against each tree, with the Revision2 archive's
  `src` in place of `src`.

| Sources | Result |
|---|---|
| Archived MANIFEST-2 (Revision2) | Ran 172; FAILED (failures=26, errors=4) |
| Corrected tree | Ran 172; OK |

This reproduces the builder's numbers. Classifying each failing test by its final
exception: 13 distinct tests fail. 11 fail on behavior (including the façade-shape
assertions), and 2 fail only because an API is missing. Those two are IR21's
secondary tests, which use the new `admission_state` observer.

Every blocking root has at least one test that fails on behavior, unlike IR12 in
round 2:

| Root | Behaviorally failing test on the archive |
|---|---|
| IR21 | The join after local close is accepted on the archive (`ContractRefusal not raised`). |
| IR22 | The third-task route test fails because `revoke` contains the command, or terminalizes it at QUEUED. |
| IR23 | Same-step re-entry recurses without bound (`RecursionError`), and effect reservation during cleanup is accepted. |
| IR24 | A dangling `(1, 0)` active serial remains. |
| IR25 | A non-worker records the diagnostic. |
| IR26 | Initial candidates are still alive after terminalization. |
| IR29 | A stub lacking `recover_migration` conforms. |

## Limits

This is deterministic single-process reference evidence. Passing suites and
failing-before runs are not closure. Every finding stays open until the reviewer
who raised it verifies its counterexample on the corrected tuple. Fresh full Code
and State review of the whole object is required, because correction 2 removed a
façade member and changed the close and join ordering.

The implementation correction count is now 2 of 2. No further correction is
available: if review round 3 reports any new P0–P2, the lane stops for the operator.
MANIFEST-3 pins this record, and its SHA-256 is recorded in the checkpoint.
