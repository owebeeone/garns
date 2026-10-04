# Garns v9-6 W1 registry/containment redesign — STATE-AXIS REVIEW, ROUND 2

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256`, manifest SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`; operator-authorized registry/containment replacement design after remediation 1; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md`, SHA-256 `f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; no Git landing asserted; redesign brief SHA-256 `afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d`; remediation plan SHA-256 `7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633`  
**Date:** 2026-10-03  
**Axis:** durable-state semantics, restart legality, containment, recovery grammar, shutdown interleavings, and fail-closed behavior. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks acceptance. All three replacement-object remediation findings and both original stopped-W1 roots are corrected on this tuple, but the adjacent cancellation and reconciliation entry points still accept values outside their declared closed enums. In particular, raw string phase/evidence values can manufacture `KNOWN_ABORTED` and release pre-commit containment. This is a **NEW BOUNDED, NON-ARCHITECTURAL root cause**. I pre-commit to GO on a revision that resolves P2-1 as specified, preserves the verified closures below, and introduces no new blocking defect.

---

## Prior-finding closure table

| Finding/root | Required disposition | Verification on current tuple | Status |
|---|---|---|---|
| Original stop: Code-3 P2-1 / initial Code P2-5 | Empty identity-only context handle; claims and ownership only in the issuer registry | `TrustedContext` remains an empty exact-instance handle with only weak-reference support. The registry-owned detached claims design, exact-instance validation, cross-issuer refusal, runtime-owned clock/epoch/task identity, and pre/post-await delivery checks are unchanged from the initial replacement tuple. | CLOSED |
| Original stop: State-3 P2-1 / initial State P2-7 | Commit-requested identities cannot leave containment without matching terminal knowledge | `finish_without_commit()` rejects commit-requested work. `resolve()` independently validates `CommitOutcome`, retains `INDETERMINATE`, rejects wrong identity and wrong-scope revision, and consumes only matching `KNOWN_COMMITTED` or `KNOWN_ABORTED`. | CLOSED |
| Replacement Code P2-1 | Reject duplicate active admission and terminal identity reuse | `WorkerCommitFence.begin()` refuses an identity present in `_begun` or `_resolved` before mutation. Repeated identical resolution remains idempotent; conflicting resolution refuses; equal client IDs in distinct qualified scopes remain distinct. | CLOSED |
| Replacement State P2-1 | Enforce the exact `CommitKnowledge` grammar at construction and resolution | `CommitOutcome` requires an exact `CommitKnowledge` member. The knowledge/revision relation is complete, and `_resolve_terminal()` revalidates bypass-constructed objects before mutation. The original fabricated-knowledge counterexample leaves the transaction unresolved. | CLOSED |
| Replacement State P2-2 | Separate worker quiescence from pending transaction knowledge | `CloseKnowledge.NONQUIESCENT` represents a running worker with zero or more pending identities. `UNRESOLVED` is reserved for quiescent close with pending identities, and `CLOSED` requires quiescence with none. Never-begun, pre-commit, indeterminate, terminally resolved, single-identity and multiple-identity cases are covered. | CLOSED |
| Prior cancellation phase/evidence closure | Only the declared closed phase/evidence relation can establish abort or indeterminacy | The relation is correct for enum-member inputs, but the helpers accept raw string values as if they were enum members. This closure does not survive malformed-input attack. | **OPEN — P2-1 below** |

## Changed-range analysis

There is no historical source snapshot or usable Git diff, so no textual before/after history was invented. Checksum inventories establish the ranges honestly.

Compared with the stopped `W1-MANIFEST-3.sha256`, exactly the six operator-authorized paths differ:

- `docs/adr/A11-trusted-context.md`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/authority.py`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

Compared with the initial replacement manifest, remediation 1 changed only:

- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

`authority.py` and A11 are unchanged from the initial replacement tuple. The current close-result changes implement the accepted architectural correction: quiescence and pending transaction knowledge are independent dimensions, and all tested close-state products return a typed result.

P2-1 is outside that corrected close-result branch but inside the integrated state contract. Its root is missing exact-enum validation at the exported recovery helpers. It is bounded and text/code-fixable; it does not require another representation or lifecycle redesign.

No unlisted path exists under `docs/adr`, `src/garns/backends/contracts`, or `tests/contracts`.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- `W1-RegistryContainmentRedesign-Brief.md`, `W1-STOP.md`, complete final `W1-ReviewCode-3.md` and `W1-ReviewState-3.md`;
- both historical W1 remediation plans, the W1 execution brief, W0 acceptance, and `docs/PRODUCT_LAYOUT.md`;
- the controlling implementation plan, provider-neutral seam, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance;
- both initial replacement-object reports and the complete consolidated replacement remediation plan;
- `W1-RegistryContainmentRedesign-DRAFT-2.md`;
- all 26 manifested files: A1–A15 and the ADR index, all eight contract modules, and both contract-test files;
- retained type, plan, value, operation, protocol, authority, publication, cancellation, reconciliation, and worker-fence semantics needed to assess the integrated tuple.

At both start and end, all 26 entries passed:

```text
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
```

The required digests matched:

```text
aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66  dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8  dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md
afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d  dev-docs/W1-RegistryContainmentRedesign-Brief.md
7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633  dev-docs/W1-RegistryContainmentRedesign-RemPlan.md
11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md
b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md
079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md
94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md
d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md
dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md
1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344  dev-docs/GarnsV9-6-W1-ExecutionBrief.md
```

The complete owned-path inventory comparison produced no differences.

The prescribed contract suite passed:

```text
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.009s

OK
```

The original and remediation counterexamples produced:

```text
malformed_outcome ValueError commit knowledge must be a declared CommitKnowledge member
CloseOutcome(knowledge=UNRESOLVED, unresolved=(tx,))

empty_close True  CloseOutcome(knowledge=CLOSED, unresolved=())
empty_close False CloseOutcome(knowledge=NONQUIESCENT, unresolved=())

duplicate_begin ContractRefusal TRANSACTION_IDENTITY_CONFLICT
terminal_reuse ContractRefusal TRANSACTION_IDENTITY_CONFLICT

terminal quiescent close     CLOSED
terminal nonquiescent close NONQUIESCENT
```

A further pure in-memory closed-grammar probe found:

```text
cancellation_outcome(tx, "queued", "not_started")
=> CommitOutcome(knowledge=KNOWN_ABORTED, transaction=tx, revision=None)

cancellation_outcome(tx, OperationPhase.QUEUED, "not_started")
=> CommitOutcome(knowledge=KNOWN_ABORTED, transaction=tx, revision=None)

reconcile(tx, "aborted")
=> CommitOutcome(knowledge=INDETERMINATE, transaction=tx, revision=None)

reconcile(tx, 0)
=> CommitOutcome(knowledge=INDETERMINATE, transaction=tx, revision=None)

reconcile(tx, False)
=> CommitOutcome(knowledge=INDETERMINATE, transaction=tx, revision=None)
```

These results arise because the state enums inherit from `str`, so raw strings with matching values compare and hash equal to enum members, while `reconcile()` treats every non-committed/non-aborted input as unresolved.

All executable probes used Python 3.14 with `-B`, `PYTHONDONTWRITEBYTECODE=1`, the prescribed cached dependency path and product `src`. They performed no file, bytecode, database, service, worker, Git, or GWZ mutation.

---

## 1. Findings

### [P2-1] Recovery helpers accept values outside their closed phase/evidence/finding enums

**Classification:** **NEW BOUNDED, NON-ARCHITECTURAL root cause.**

**Location:** `src/garns/backends/contracts/state.py:127-166`, specifically the absence of exact-type validation at the start of `cancellation_outcome()` and `reconcile()`. The behavior contradicts the closed grammar stated in `docs/adr/A7-isolation-retry.md` and the exact-enum defensive boundary now enforced by `CommitOutcome` at `state.py:79-92`.

**Violated invariant:** Only declared `OperationPhase`, `AbortEvidence`, and `ReconcileFinding` members may participate in recovery-state transitions. Malformed adapter, deserialization, or implementation values must refuse before producing durable knowledge. In particular, caller-supplied strings must not establish authoritative abort and release containment.

**Reproduction/state sequence:**

1. Create a `WorkerCommitFence` and `begin(tx)`.
2. Call:

   ```python
   outcome = cancellation_outcome(tx, "queued", "not_started")
   ```

3. Because `OperationPhase` and `AbortEvidence` are `str` enums, the raw-string tuple compares equal to the declared `(QUEUED, NOT_STARTED)` tuple.
4. The helper returns an exact, otherwise valid `CommitOutcome(KNOWN_ABORTED, tx)`.
5. Pass it to:

   ```python
   fence.finish_without_commit(tx, outcome)
   ```

6. `_resolve_terminal()` correctly validates the resulting `CommitOutcome`, records it as terminal, and removes `tx` from `_begun`.
7. `close_outcome(True)` can now return `CLOSED`, even though authoritative phase/evidence enum members were never supplied.

A mixed malformed pair such as `(OperationPhase.QUEUED, "not_started")` succeeds identically.

The same root is visible in `reconcile()`: raw strings, integers, booleans, and arbitrary objects that are neither exact `COMMITTED` nor `ABORTED` members fall through to a valid `INDETERMINATE` outcome rather than being rejected. That direction is fail-closed, but it can strand an identity and obscures an invalid adapter state instead of preserving the promised closed grammar.

**Impact:** A malformed or stringly typed cancellation adapter can manufacture known-abort evidence and release pre-commit containment. Malformed reconciliation findings silently become indeterminate, causing avoidable stuck recovery and losing diagnosability. The newly hardened `CommitOutcome` boundary cannot detect the provenance error because `cancellation_outcome()` has already converted the malformed inputs into a legitimate enum-backed terminal outcome.

**Required correction:** At entry to `cancellation_outcome()`, require:

```python
type(phase) is OperationPhase
type(evidence) is AbortEvidence
```

At entry to `reconcile()`, require:

```python
type(finding) is ReconcileFinding
```

Reject all other values before constructing an outcome. Preserve the existing closed relation for exact members. Prefer one explicit invalid-state exception class consistently; no new state or lifecycle representation is needed.

**Closure/regression test:** Exhaustively test:

- every exact `OperationPhase × AbortEvidence` pair;
- matching raw strings for every enum value;
- integers, booleans, arbitrary objects, and foreign enum members;
- every exact `ReconcileFinding`;
- matching raw reconciliation strings and other malformed values.

For malformed cancellation inputs, assert refusal and prove no terminal outcome can be passed to `finish_without_commit()`. For malformed reconciliation inputs, assert refusal rather than conversion to `INDETERMINATE`. Retain the valid rules: queued/not-started and rollback-requested/rollback-confirmed yield known abort; uncertain statement/write/rollback/commit states remain indeterminate; committed reconciliation requires a same-scope revision; aborted reconciliation has none; unresolved findings cannot carry a revision.

---

## 2. Invariant analysis

The following attacks failed to identify another finding:

- **Malformed terminal outcome:** unknown string, integer, boolean, object, or bypass-constructed `CommitOutcome` knowledge refuses before any fence mutation.
- **Knowledge/revision product:** exact known commit requires a same-scope revision; known abort and indeterminate prohibit revisions.
- **Original unsafe finish:** commit-requested work cannot pass through `finish_without_commit()`.
- **Identity-bound resolution:** wrong transaction and wrong-scope revision refuse without changing `_begun`, `_commit_requested`, or `_resolved`.
- **Indeterminate containment:** an indeterminate result leaves both begun and commit-requested identity state intact.
- **Duplicate/reused admission:** duplicate active and terminally reused identities refuse before mutation. Qualified identities with the same client component in different scopes remain distinct.
- **Repeated resolution:** identical terminal resolution is idempotent; conflicting resolution refuses.
- **Late commit fence:** `start_shutdown()` prevents any begun pre-commit command from newly requesting commit.
- **Close-state product:** quiescent/empty returns `CLOSED`; quiescent/pending returns `UNRESOLVED`; nonquiescent returns `NONQUIESCENT` with zero or more pending identities. No accepted combination throws or invents an identity.
- **Final outcome versus worker state:** a terminally resolved transaction is not relabeled unresolved merely because the worker remains nonquiescent.
- **Multiple pending identities:** pre-commit and commit-requested-indeterminate identities remain qualified, unique, and all listed in close outcomes.
- **Registry containment:** the caller handle remains empty and has no ordinary attribute route to claims, issuer, registry, validity, capability, scope, identity, or task owner.
- **Authority validity:** exact registered identity, runtime clock, epoch, scope, capability, invalidation, and task-object identity remain enforced.
- **Subscription delivery:** the sole bound iterator validates before the awaited read and again before delivery; expiry, epoch change, invalidation, task change, close, and renewal prevent stale delivery.
- **Publication:** transaction identity plus payload digest remains idempotent and conflict-detecting across generation and retention changes.
- **Migration:** metadata-only and data-changing outcomes remain disjoint; successful data-changing migration requires exact request, binding, scope, generation, transaction identity, digest, and nonempty effects.
- **Snapshot/replay and retention:** cursor scope/generation, watermark ordering, overflow/refetch, retained floor, and generation mismatch remain explicitly represented.
- **Immutable values:** parameters, snapshots, deliveries, mutations, and ledger effects detach supported nested input structures.
- **Protocol parity:** both backends retain the same async-facing contract and explicit pre-effect capability refusal.
- **Conditional-boundary hygiene:** no modified source introduces conditional compilation or an applicable unbraced C-style control-flow body.

External capture W6/P6, cryptographic providers, arbitrary host-memory secrecy, actual database/runtime/worker implementations, restart fault cuts, W2 exhaustive algebra, and W3 public naming remain correctly deferred rather than counted as passing evidence.

---

## 3. Risks and next action

The remaining below-finding-bar risk is evidentiary: this tuple contains pure contracts, reference models, and conforming fakes. It does not establish real worker quiescence, restart durability, database commit reconciliation, SQLite interruption behavior, PostgreSQL atomicity, migration crash safety, or filesystem ordering. Those remain later implementation gates.

The single next action is a bounded exact-enum validation correction for P2-1 in the recovery helpers, with the malformed-input regressions specified above, followed by a focused State re-verdict on a newly pinned complete 26-file tuple. The correction must preserve the now-closed registry, identity-admission, malformed-`CommitOutcome`, and independent close-state counterexamples.
