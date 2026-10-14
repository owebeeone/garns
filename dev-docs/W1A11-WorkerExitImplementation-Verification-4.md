# Worker exit implementation manager verification 4

Date: 2026-10-05. Owner: manager.

Status: candidate after the one-line correction 3, verified for the two-reviewer
re-check. This is not accepted source.

- **Authority.** The operator authorized correction 3 as an exception to the gate,
  under [RemPlan-3](W1A11-WorkerExitImplementation-RemPlan-3.md).
- **Builder.** One fresh Sonnet subagent worked under
  [BuilderPrompt-4](W1A11-WorkerExitImplementation-BuilderPrompt-4.md). Its
  transcript shows `claude-sonnet-5-5` from 2026-10-04 23:45Z to 23:54Z.
- **Testimony.** The builder's account is filed verbatim as
  [DRAFT-4](W1A11-WorkerExitImplementation-DRAFT-4.md), SHA-256
  `cbd17c1ba053c0cbccfc0d4a2413e86b3efdb5599205fc4612f7a63ab8718348`.

## Delta

**MANIFEST-3** `9a9f8b2a…` is unchanged, and 138 of its 141 entries still verify
against live. The 3 changed entries are exactly BuilderPrompt-4's allowlist:

| Path | Change |
|---|---|
| `src/garns/backends/contracts/lifetime_reference.py` | `diff` against the Revision3 copy prints only `664c664`: the success gate now reads `if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:` |
| `tests/contracts/test_worker_exit_contracts.py` | New class `CleanupInFlightSuccessExitTests` with 3 tests, run as 5 subtest cases. Nothing removed. |
| `dev-docs/W1A11-WorkerExitImplementation.md` | One added row, for IR31. |

**Other guards.** All pass:

| Guard | Result |
|---|---|
| ReadOnly | 741 OK |
| Inputs | 31 OK |
| Baseline | 20 OK |
| RemInputs-3 | 13 OK |
| Revision3, verified from inside the archive | 141 OK |
| Bytecode files | none |

## Reproduced gates

| CPython | Focused | Full | Product |
|---|---:|---:|---:|
| 3.11.14 | 190 | 293 | 5 PASS |
| 3.12.12 | 190 | 293 | 5 PASS |
| 3.13.12 | 190 | 293 | 5 PASS |
| 3.14.3 | 190 | 293 | 5 PASS |

- All 12 commands exited zero.
- The inherited SQLite warnings stayed visible: 116 lines on 3.13 and 140 on 3.14.
- Exact commands and complete outputs are in
  [VerificationLogs-4](W1A11-WorkerExitImplementation-VerificationLogs-4.md).

## Failing-before, reproduced

**Method.** The contract test modules were copied into a scratchpad package with
an empty `tests/__init__.py`. The new class was then run on Python 3.14 against
each tree.

| Sources | Result |
|---|---|
| Archived MANIFEST-3 (Revision3) | FAILED (failures=5); every case fails with "success exit was accepted from inside the final cleanup action" |
| Corrected tree | OK |

This is a behavioral failure: the defect itself, not a missing API.

## Limits

- **Evidence.** This is deterministic single-process reference evidence. Passing
  tests are not closure.
- **Re-check.** IR31 closes only when the two round-3 full reviewers verify their
  counterexamples on MANIFEST-4.
- **Out of scope.** The implementation record's older IR23 wording and DRAFT-3 are
  unchanged, as the one-line scope required. ReviewCode-3 P2-1 asked for those
  wording corrections; they are recorded for W3.
- **Pinning.** MANIFEST-4 pins this record. Its SHA-256 is in the checkpoint.
