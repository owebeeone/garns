# Garns v9-6 W1 registry/containment redesign — STATE-AXIS REVIEW, ROUND 3

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-3.sha256`, manifest SHA-256 `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`; focused re-verdict after replacement-object remediation 2; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT-3.md`, SHA-256 `458aeea7dd184a96af413d2550b6dffb54ced623a6a4cd406468e94f461c6128`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; no Git landing asserted; redesign brief SHA-256 `afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d`; remediation plan 2 SHA-256 `f96ae011016e382c53d439311275b7f1c9e6f6ca5c62bef4f0423e23c269c2ed`  
**Date:** 2026-10-03  
**Axis:** durable-state semantics, recovery grammar, containment, shutdown interleavings, and fail-closed behavior. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — no P0, P1, P2, or P3 State findings. State-2 P2-1 is closed: malformed phase, evidence, and reconciliation values now refuse before producing commit knowledge, while the valid closed relation and all earlier containment closures remain intact. No new architectural root cause was found.

---

## Prior-finding closure table

| Finding/root | Required disposition | Verification on current tuple | Status |
|---|---|---|---|
| State-2 P2-1 | Require exact `OperationPhase`, `AbortEvidence`, and `ReconcileFinding` members before producing knowledge | `cancellation_outcome()` performs exact-type guards before relation evaluation. `reconcile()` performs an exact finding guard before branching. Raw strings, integers, booleans, objects, and foreign enums refuse. The original raw-string known-abort manufacture no longer produces an outcome, and the begun identity remains contained. | **CLOSED** |
| Replacement Code P2-1 | Refuse duplicate active admission and terminal transaction-identity reuse | `WorkerCommitFence.begin()` still refuses identities present in `_begun` or `_resolved` before mutation. Repeated resolution remains idempotent; conflicting resolution refuses; qualified scopes remain distinct. | CLOSED |
| Replacement State P2-1 | Enforce exact `CommitKnowledge` and its revision relation | `CommitOutcome` still requires an exact member. Known commit requires a same-scope revision; known abort and indeterminate reject revisions. Resolution revalidates bypass-constructed outcomes before mutation. | CLOSED |
| Replacement State P2-2 | Represent worker quiescence independently from pending transaction knowledge | `CLOSED`, `UNRESOLVED`, and `NONQUIESCENT` retain the exhaustive corrected product. Nonquiescent workers may carry zero or more pending identities; quiescent pending work remains unresolved; terminally resolved transactions are not relabeled uncertain. | CLOSED |
| Original stop: State-3 P2-1 / initial State P2-7 | Commit-requested identities cannot disappear without matching terminal knowledge | `finish_without_commit()` still rejects commit-requested work. Indeterminate resolution retains containment; matching committed or aborted resolution clears it; wrong identity and wrong-scope revision refuse. | CLOSED |
| Original stop: Code-3 P2-1 / initial Code P2-5 | Empty identity-only trusted-context handle with registry-owned claims | `authority.py` and A11 are byte-identical to the already reviewed replacement tuple. The empty exact-instance handle, issuer registry, runtime-owned clock/epoch/task checks, and post-await validation remain intact. | CLOSED |
| Earlier cancellation/reconciliation grammar | Closed valid relation with no invented abort or commit | Every exact phase/evidence pair is tested. Only queued/not-started and rollback-requested/rollback-confirmed yield known abort; the declared uncertain pairs yield indeterminate; incompatible pairs refuse. Committed reconciliation requires a same-scope revision; aborted and unresolved findings reject supplied revisions. | CLOSED |

## Changed-range analysis

The checksum inventory comparison against `W1-RegistryContainmentRedesign-MANIFEST-2.sha256` shows exactly two changed files:

- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

The other 24 manifested files are byte-identical to State round 2. The complete inventory under `docs/adr`, `src/garns/backends/contracts`, and `tests/contracts` matches the 26-file manifest with no extra or missing path.

The source change is bounded to entry validation and explicit revision rejection:

- `cancellation_outcome()` now requires exact `OperationPhase` and `AbortEvidence` members before consulting the unchanged relation.
- `reconcile()` now requires an exact `ReconcileFinding`.
- Aborted reconciliation explicitly rejects a supplied revision; unresolved reconciliation continues to reject one.
- Function signatures, valid return grammar, worker close algebra, lifecycle states, and call graph are unchanged.

The matching tests add exhaustive malformed-shape coverage and preserve the full valid Cartesian phase/evidence relation. No ADR, protocol, authority, backend, worker implementation, database behavior, dependency, or public surface changed.

The remediation plan records a separate nonblocking Code P3 follow-up for W3. It was deliberately unchanged here and does not constitute a State-axis blocker or broaden this correction.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md` and product `AGENTS.md`;
- the complete focused remediation plan, `W1-RegistryContainmentRedesign-RemPlan-2.md`;
- the complete builder testimony, `W1-RegistryContainmentRedesign-DRAFT-3.md`;
- the current manifest and changed `state.py` and contract-test ranges;
- the prior State review, its exact P2-1 counterexamples, and the legitimate prior replacement reports/remediation records already reviewed in round 2;
- the unchanged integrated tuple semantics needed to recheck authority, publication, migration, cancellation, reconciliation, identity admission, terminal resolution, and shutdown containment.

At both start and end:

```text
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST-3.sha256
```

reported `OK` for all 26 paths.

The required hashes matched at both boundaries:

```text
95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549  dev-docs/W1-RegistryContainmentRedesign-MANIFEST-3.sha256
458aeea7dd184a96af413d2550b6dffb54ced623a6a4cd406468e94f461c6128  dev-docs/W1-RegistryContainmentRedesign-DRAFT-3.md
f96ae011016e382c53d439311275b7f1c9e6f6ca5c62bef4f0423e23c269c2ed  dev-docs/W1-RegistryContainmentRedesign-RemPlan-2.md
afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d  dev-docs/W1-RegistryContainmentRedesign-Brief.md
11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md
b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md
079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md
94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md
d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md
dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md
1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344  dev-docs/GarnsV9-6-W1-ExecutionBrief.md
```

The prescribed focused suite passed:

```text
.............................................
----------------------------------------------------------------------
Ran 45 tests in 0.010s

OK
```

The original State-2 counterexamples now produce:

```text
cancellation_outcome(tx, "queued", "not_started")
ValueError: cancellation requires declared phase and evidence members

cancellation_outcome(tx, OperationPhase.QUEUED, "not_started")
ValueError: cancellation requires declared phase and evidence members

cancellation_outcome(tx, "queued", AbortEvidence.NOT_STARTED)
ValueError: cancellation requires declared phase and evidence members

still_contained:
CloseOutcome(knowledge=UNRESOLVED, unresolved=(tx,))
```

Malformed reconciliation values now refuse:

```text
"aborted"          -> ValueError
"still_in_flight"  -> ValueError
0                  -> ValueError
False              -> ValueError
object()           -> ValueError
foreign str enum   -> ValueError
```

The complete valid relation remains:

```text
queued / not_started
    -> KNOWN_ABORTED

rollback_requested / rollback_confirmed
    -> KNOWN_ABORTED

declared uncertain statement/write/rollback/commit pairs
    -> INDETERMINATE

all other exact phase/evidence pairs
    -> ValueError

COMMITTED + same-scope revision
    -> KNOWN_COMMITTED

ABORTED + no revision
    -> KNOWN_ABORTED

STILL_IN_FLIGHT or NOT_FOUND_NOT_FINAL + no revision
    -> INDETERMINATE
```

A supplied revision with `ABORTED`, `STILL_IN_FLIGHT`, or `NOT_FOUND_NOT_FINAL` refuses.

Exported signatures remain unchanged:

```text
cancellation_outcome(
    transaction: TransactionIdentity,
    phase: OperationPhase,
    evidence: AbortEvidence
) -> CommitOutcome

reconcile(
    transaction: TransactionIdentity,
    finding: ReconcileFinding,
    revision: RevisionCursor | None = None
) -> CommitOutcome
```

Retained shutdown probes confirmed:

```text
commit-requested finish_without_commit -> ValueError
indeterminate + nonquiescent           -> NONQUIESCENT(tx)
matching known abort + quiescent       -> CLOSED
matching known abort + nonquiescent    -> NONQUIESCENT()
duplicate active begin                 -> TRANSACTION_IDENTITY_CONFLICT
terminal identity reuse                -> TRANSACTION_IDENTITY_CONFLICT
```

All executable probes used Python 3.14 with `-B`, `PYTHONDONTWRITEBYTECODE=1`, the prescribed cached dependency, and product `src`. No file, bytecode, database, service, worker, Git, or GWZ mutation occurred.

---

## 2. Invariant analysis

The focused correction held under the following attacks:

- **Raw-string abort manufacture:** rejected before a `CommitOutcome` exists; the begun identity remains contained.
- **Mixed enum/string inputs:** rejected regardless of which phase/evidence component is malformed.
- **Foreign enum resemblance:** rejected even when a foreign string enum has the same textual value.
- **Malformed reconciliation:** rejected rather than silently converted to indeterminate.
- **Revision misuse:** aborted and unresolved findings cannot carry a revision; committed findings require one in the exact transaction scope.
- **Valid closed relation:** all exact phase/evidence combinations retain their prior classification.
- **Fail-closed direction:** invalid inputs neither create terminal knowledge nor mutate the worker fence.
- **Original stopped-W1 containment:** commit-requested work cannot be cleared through the pre-commit completion path.
- **Indeterminate retention:** unresolved commit knowledge remains listed through repeated shutdown and nonquiescent close.
- **Terminal resolution:** matching final knowledge clears transaction containment without falsely claiming worker quiescence.
- **Identity admission:** active duplicates and terminal reuse refuse before new work is admitted.
- **Close grammar:** worker quiescence and transaction knowledge remain independent and total for zero, one, or multiple pending identities.
- **Registry authority:** the empty-handle registry design and runtime-owned validation barriers are unchanged.
- **Publication and migration:** qualified identity, idempotency/conflict checks, generation handling, and migration effect coupling are unchanged and remain covered by the passing regressions.
- **Conditional-boundary hygiene:** the modified Python files introduce no conditional-compilation boundary issue or applicable unbraced C-style control flow.

No new architectural root cause was found.

Explicit deferrals remain correctly bounded: external capture W6/P6, cryptographic providers, arbitrary host-process memory secrecy, actual backend/worker/database implementation, restart and fault-cut proof, W2 exhaustive algebra, and W3 public names/Surface are not accepted by this review.

---

## 3. Risks and next action

The residual risk is evidentiary rather than a defect in this W1 object: the state helpers and fence are pure reference models. Passing tests do not prove real worker-thread quiescence, durable restart reconciliation, SQLite interruption behavior, PostgreSQL atomicity, or database fault cuts. Those remain assigned to later implementation gates.

The State-axis next action is acceptance of this focused correction. The lane owner may merge this GO with the independent Code-axis verdict for the exact same manifest. If the other axis also reports GO under its contract, the replacement W1 tuple can proceed to manager acceptance; this report alone does not authorize W2, Git landing, or implementation work.
