# W1 Registry/Containment Redesign — ORIGINATING CODE FINDING CLOSURE

**Closure object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256`, manifest SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`  
**Controlling remediation:** `dev-docs/W1-RegistryContainmentRedesign-RemPlan.md`, SHA-256 `7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633`  
**Builder testimony:** `dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md`, SHA-256 `f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8`  
**Date:** 2026-10-03  
**Role:** originating Code reviewer, focused read-only closure of Code P2-1. This is not a fresh whole-object review and does not rely on or inspect current-round reviewer reports.

**Closure verdict: VERIFIED — Code P2-1 is CLOSED.** The original duplicate-active and terminal-identity-reuse counterexamples now refuse before state mutation. Repeated resolution remains idempotent for the original operation, conflicting resolution refuses, and equal client IDs in distinct qualified scopes remain independently admissible. The two stopped-object counterexamples also remain closed.

---

## Closure table

| Finding | Required disposition | Original counterexample re-run | Status |
|---|---|---|---|
| Code P2-1 | Refuse duplicate active or terminally reused transaction identity at worker admission, before mutation; retain idempotent original resolution and qualified-scope distinction | Both admission attacks now return `TRANSACTION_IDENTITY_CONFLICT`; snapshots of `_begun`, `_commit_requested`, and `_resolved` are unchanged across each refusal. Repeated identical resolution succeeds, conflicting resolution refuses, and equal client IDs in different scopes remain distinct. | **CLOSED** |
| Code-3 P2-1 / initial Code P2-5 | Caller-held context remains an empty identity handle with no claim or issuer route | Handle still has only `__weakref__`; canaries remain absent from ordinary diagnostics; copying, serialization and dataclass helpers refuse; cross-issuer and reconstructed handles remain unauthorized. | **RETAINED CLOSED** |
| State-3 P2-1 / initial State P2-7 | Commit-requested work cannot be erased through pre-commit completion | `finish_without_commit()` still refuses a commit-requested identity without changing fence state; the identity remains present in the typed nonquiescent outcome. | **RETAINED CLOSED** |

## Changed-range confirmation

Compared with the initial redesign manifest, four paths changed:

- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`

The registry-only authority implementation and A11 contract are byte-identical to the reviewed redesign. The correction is consistent with the accepted disposition:

- `WorkerCommitFence.begin()` now checks both `_begun` and `_resolved` before insertion.
- Active or terminal identity reuse raises typed `TRANSACTION_IDENTITY_CONFLICT`.
- Rejection occurs before any fence collection is mutated.
- Existing resolution logic still returns idempotently for an identical terminal outcome and rejects a conflicting terminal outcome.
- `TransactionIdentity` equality remains qualified by world/deployment scope as well as client ID.
- The close grammar now represents nonquiescence independently; this shared change is assigned to the fresh whole-object reviewers, not adjudicated here beyond confirming it does not reopen my finding.

The scoped path inventory exactly matched all 26 manifest entries.

## Evidence

Start and end tuple verification produced the same values:

```text
7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633  dev-docs/W1-RegistryContainmentRedesign-RemPlan.md
f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8  dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md
aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66  dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
```

Both executions of:

```sh
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
```

reported all 26 files `OK`.

The prescribed focused suite passed:

```text
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.010s

OK
```

### Original duplicate-active counterexample

Executed sequence:

```python
fence.begin(tx)
before = snapshot(fence)
fence.begin(tx)
```

Observed:

```text
duplicate_active transaction_identity_conflict
duplicate_unchanged True
CloseOutcome(knowledge=UNRESOLVED, unresolved=(tx,))
```

The second admission refused before mutation. The original operation remained represented exactly once.

### Original terminal-reuse counterexample

The first operation was committed and resolved, then resolved identically again. A conflicting abort resolution refused. A new `begin(tx)` was then attempted.

Observed:

```text
conflict ValueError transaction already has a different terminal outcome
terminal_reuse transaction_identity_conflict
terminal_unchanged True
CloseOutcome(knowledge=CLOSED, unresolved=())
```

The original repeated resolution remained idempotent. Terminal identity reuse refused before adding new work, so the prior stranded-identity trace is unreachable.

### Qualified-scope regression

Two transaction identities used the same client ID under distinct qualified scopes.

Observed:

```text
qualified_distinct True
```

Both were admitted and independently present in the unresolved set.

### Retained stopped-object closures

Commit-requested pre-commit completion:

```text
finish_commit_requested ValueError
finish_unchanged True
CloseOutcome(knowledge=NONQUIESCENT, unresolved=(tx,))
```

Opaque handle:

```text
handle_slots ('__weakref__',)
canaries_visible False
copy refused
deepcopy refused
pickle refused
vars refused
asdict refused
cross refused
reconstructed refused
```

## Conclusion

Code P2-1 is independently closed on manifest `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`. Its exact counterexamples no longer reproduce, the correction preserves state on refusal, and the relevant retained regressions pass.

This testimony closes only the originating Code finding. It does not accept the redesign or W1, adjudicate the current shared close-grammar review, establish backend/runtime behavior, or authorize W2.
