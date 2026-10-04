# W1 Registry/Containment Redesign — Originating State Finding Closure

**Review object:** corrected 26-file tuple in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256`, SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`  
**Controlling draft:** `dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md`, SHA-256 `f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8`  
**Remediation plan:** `dev-docs/W1-RegistryContainmentRedesign-RemPlan.md`, SHA-256 `7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633`  
**Date:** 2026-10-03  
**Role:** originating State reviewer, focused read-only closure verification. This testimony addresses only the original State P2-1 and P2-2 counterexamples, their regression coverage and preservation of the preceding shutdown-stop closure. It is not a new whole-object review and uses no current-round reviewer report.

**Focused verdict: CLOSURE VERIFIED** — State P2-1 and State P2-2 are closed on the exact corrected tuple. The preceding stopped-W1 unsafe-finish counterexample also remains closed. No open finding remains within this focused mandate.

---

## Prior-finding closure table

| ID | Required correction | Independent counterexample result | Status |
|---|---|---|---|
| State P2-1 | Enforce the closed `CommitKnowledge` grammar at construction and again before resolution mutation; malformed knowledge must preserve containment | Unknown strings including `"fabricated"` and `"indeterminate"`, integers, booleans and an arbitrary object all refused at construction. A bypass-constructed malformed `CommitOutcome` also refused during `resolve()`. `_begun`, `_commit_requested` and `_resolved` remained unchanged, and the qualified identity remained present in the typed nonquiescent outcome. | **CLOSED** |
| State P2-2 | Represent worker quiescence independently of pending transaction knowledge, including nonquiescent states with zero identities | Never-begun/nonquiescent and terminally-resolved/nonquiescent workers both returned `NONQUIESCENT` with an empty identity tuple. Pre-commit and commit-requested-indeterminate work returned `NONQUIESCENT(ids)` while running and `UNRESOLVED(ids)` when quiescent. Terminally resolved work returned `NONQUIESCENT(())` while running and `CLOSED` only when quiescent. No reachable tested state raised or invented an identity. | **CLOSED** |
| State-3 P2-1 / initial State P2-7 | Commit-requested work must not leave containment through `finish_without_commit()` | The original trace still refuses: after begin, commit request and shutdown, `finish_without_commit(tx, KNOWN_ABORTED(tx))` raises and the exact qualified identity remains contained. `INDETERMINATE` also remains contained; only matching final resolution clears it. | **CLOSED, PRESERVED** |

## Changed-range verification

Comparison of the initial redesign manifest with the corrected manifest found exactly four changed paths:

- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`

The registry-only authority implementation and A11 remained byte-identical. The correction therefore stayed within the authorized redesign boundary and did not disturb the already-verified empty-handle design.

The relevant implementation changes are:

- `CommitOutcome.__post_init__()` delegates to `_validate_commit_outcome()`.
- `_validate_commit_outcome()` requires exact `CommitKnowledge`, `TransactionIdentity` and `RevisionCursor` types and enforces the complete knowledge/revision relation.
- `WorkerCommitFence._resolve_terminal()` revalidates the outcome immediately before any containment mutation.
- `CloseKnowledge` now includes `NONQUIESCENT`.
- `close_outcome()` returns:
  - `NONQUIESCENT` with zero or more pending identities when the worker is not quiescent;
  - `UNRESOLVED` with one or more identities when quiescent but pending knowledge remains;
  - `CLOSED` only when quiescent with no pending identities.
- A8 and the ADR lifecycle diagram now state the same exhaustive close grammar.

These changes match the remediation dispositions for State P2-1 and P2-2.

---

## 0. Evidence base

At both the start and end of this focused verification:

```text
7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633  dev-docs/W1-RegistryContainmentRedesign-RemPlan.md
f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8  dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md
aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66  dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
```

The manifest verification reported `OK` for all 26 files at both boundaries.

I read the complete remediation plan and corrected draft, the corrected manifest, the changed state model, focused regressions, A8 and the ADR lifecycle diagram. I did not read or rely on current-round Code or State reports.

The prescribed focused suite passed:

```text
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.030s

OK
```

All commands used Python 3.14 with `-B`, `PYTHONDONTWRITEBYTECODE=1`, the prescribed cached dependency path and product `src`. No file, bytecode, Git state, service, database or backend was modified.

---

## 1. Closure evidence

### State P2-1 — malformed commit knowledge

The original defect accepted:

```python
CommitOutcome("fabricated", tx)
```

and then removed the commit-requested identity during `resolve()`.

The corrected constructor rejected each of:

```text
"fabricated"
"indeterminate"
0
1
False
True
object()
```

The second validation boundary was attacked by bypassing the frozen dataclass constructor with `object.__new__`, installing malformed fields through `object.__setattr__`, and passing that object to `resolve()`. Resolution raised `ValueError`.

A before/after snapshot verified all three containment structures were unchanged:

```text
malformed-preserved True
CloseOutcome(
    knowledge=<CloseKnowledge.NONQUIESCENT: 'nonquiescent'>,
    unresolved=(TransactionIdentity(..., client_id='tx'),)
)
```

The implementation also retains the valid relation:

- `KNOWN_COMMITTED` requires a same-scope revision.
- `KNOWN_ABORTED` forbids a revision.
- `INDETERMINATE` forbids a revision and remains contained.

The original counterexample no longer reaches mutation or terminal close.

### State P2-2 — zero-identity nonquiescence

The two original failing states now produce typed results:

```text
empty-running
CloseOutcome(
    knowledge=<CloseKnowledge.NONQUIESCENT: 'nonquiescent'>,
    unresolved=()
)

terminal-running
CloseOutcome(
    knowledge=<CloseKnowledge.NONQUIESCENT: 'nonquiescent'>,
    unresolved=()
)
```

Once the terminally resolved worker becomes quiescent:

```text
terminal-quiet
CloseOutcome(
    knowledge=<CloseKnowledge.CLOSED: 'closed'>,
    unresolved=()
)
```

The independent phase matrix produced:

```text
precommit:
  running -> NONQUIESCENT(tx)
  quiet   -> UNRESOLVED(tx)

indeterminate:
  running -> NONQUIESCENT(tx)
  quiet   -> UNRESOLVED(tx)

known committed:
  running -> NONQUIESCENT()
  quiet   -> CLOSED()
```

Thus quiescence and transaction knowledge are represented independently. A final transaction is not relabeled unresolved merely because its worker still runs, and a running worker without pending transactions is not falsely closed.

### Preservation of the stopped-W1 shutdown correction

After begin, commit request and shutdown, the original unsafe completion call still raises:

```python
finish_without_commit(
    tx,
    CommitOutcome(CommitKnowledge.KNOWN_ABORTED, tx),
)
```

The resulting close state remained:

```text
CloseOutcome(
    knowledge=<CloseKnowledge.NONQUIESCENT: 'nonquiescent'>,
    unresolved=(TransactionIdentity(..., client_id='tx'),)
)
```

Wrong-identity resolution, indeterminate retention, matching final resolution, repeated identical resolution and conflicting terminal resolution remain covered by the focused suite. The correction did not reopen the stopped-W1 containment defect.

---

## 2. Focused invariant result

The corrected tuple satisfies the invariants attacked by the originating report:

- malformed final knowledge cannot clear containment;
- constructor bypass does not bypass resolution validation;
- only the declared terminal knowledge members can resolve work;
- indeterminate knowledge retains the exact qualified identity;
- worker quiescence does not imply transaction finality;
- transaction finality does not imply worker quiescence;
- nonquiescent workers with no pending identities have a typed, nonterminal state;
- `CLOSED` requires both quiescence and no pending identity;
- commit-requested work cannot use the pre-commit completion path;
- no tested recovery path invents an identity, invents a final outcome or erases unresolved knowledge.

The focused tests are pure reference-model evidence. They do not establish restart durability, real SQLite worker containment, database reconciliation or fault-cut behavior.

---

## 3. Disposition and next action

State P2-1 and State P2-2 are independently closed on manifest SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`. The prior shutdown-stop correction remains intact.

No further remediation is required for these originating State findings. The corrected shared close grammar still requires the separately assigned fresh peer-blind whole-object Code/State verdicts before manager acceptance; this focused closure testimony does not substitute for that gate.
