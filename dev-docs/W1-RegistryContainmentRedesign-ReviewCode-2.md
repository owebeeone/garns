# W1 Registry/Containment Redesign — CODE-AXIS REVIEW, ROUND 2

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256`, manifest SHA-256 `aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`; operator-authorized registry/containment replacement design after remediation 1; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT-2.md`, SHA-256 `f9710fab84302894b615ac32271fa370336d6b5f5c327ed4ea915690c594c8d8`; source writes stopped  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; redesign brief SHA-256 `afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d`; remediation plan SHA-256 `7406e007cdcaf9cf7958a8244df955e106001ac048b8fab2202b1c63e45bb633`; sources read directly from the hash-pinned working tree  
**Date:** 2026-10-03  
**Axis:** architecture, interfaces, call graphs, and compatibility reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, or P2 findings remain. All three prior replacement-object findings and both original stopped-W1 roots close on the corrected tuple. One bounded P3 lifecycle-validation defect remains and does not block this gate.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Initial replacement Code P2-1 | Refuse duplicate active admission and terminal identity reuse while preserving resolution idempotency | `WorkerCommitFence.begin()` checks both `_begun` and `_resolved` before mutation. The original duplicate-active and terminal-reuse sequences now raise `TRANSACTION_IDENTITY_CONFLICT`; repeated identical resolution remains idempotent, conflicting resolution refuses, and equal client IDs in different qualified scopes remain distinct. | **CLOSED** |
| Initial replacement State P2-1 | Make `CommitOutcome` a closed exact-member grammar and revalidate it at resolution | Construction rejects strings, integers, booleans and arbitrary objects as knowledge. A bypass-constructed malformed instance is rejected by `_validate_commit_outcome()` before fence mutation. Known commit requires a same-scope revision; known abort and indeterminate prohibit revisions. | **CLOSED** |
| Initial replacement State P2-2 | Separate worker quiescence from unresolved transaction knowledge | `CloseKnowledge.NONQUIESCENT` now represents a running worker with zero or more unresolved identities; `UNRESOLVED` is reserved for quiescent close with nonempty pending identities; `CLOSED` is returned only for quiescent close with none. Never-begun, terminally resolved, pre-commit, indeterminate, zero-, one-, and multiple-identity cases all return typed outcomes. | **CLOSED** |
| Stopped W1 Code-3 P2-1 / initial Code P2-5 | Keep claims solely in issuer-owned registry state behind an identity-only caller handle | `TrustedContext` retains only `__weakref__`. It has no claims, identifier, issuer, registry or capability field. Copy, deepcopy, pickle/reduction, dataclass conversion, `vars`, reinitialization, counterfeit construction and cross-issuer validation refuse. Canary data is absent from caller-visible handle diagnostics. | **CLOSED** |
| Stopped W1 State-3 P2-1 / initial State P2-7 | Do not erase commit-requested work without an identity-matching final result | `finish_without_commit()` refuses active commit-requested work. Wrong identity and wrong-scope revision refuse before mutation; indeterminate remains contained; matching committed or aborted resolution clears containment; acknowledgement-loss and repeated-reconciliation traces preserve the identity until terminal knowledge exists. | **CLOSED** |

## Changed-range analysis

Checksum-inventory comparison against stopped `W1-MANIFEST-3.sha256` shows exactly the six operator-authorized redesign paths changed:

- `docs/adr/A11-trusted-context.md`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/authority.py`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

The other 20 manifested files are byte-identical to the stopped tuple. The complete path inventory under `docs/adr`, `src/garns/backends/contracts`, and `tests/contracts` matches the 26 manifest entries with no extra or missing paths.

Comparison against the initial replacement manifest shows remediation 1 changed only:

- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

`authority.py` and A11 are unchanged from the initial replacement tuple, as required.

The remediation changes implement all three accepted dispositions: duplicate identity admission is rejected, terminal outcome knowledge is exact and revalidated, and the close algebra is now the full quiescence × transaction-knowledge product. No change falls outside the authorized six-file redesign boundary. The P3 below is a localized ordering defect in the retained resolution helper, not a **NEW ARCHITECTURAL root cause**.

---

## 0. Evidence base

I read in full:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical prompt template;
- `W1-RegistryContainmentRedesign-Brief.md`, both redesign drafts, both prior replacement reports, and `W1-RegistryContainmentRedesign-RemPlan.md`;
- `W1-STOP.md`, `W1-ReviewCode-3.md`, `W1-ReviewState-3.md`, `W1-RemPlan.md`, `W1-RemPlan-2.md`, and the W1 execution brief;
- the accepted implementation plan, provider-neutral seam record, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance, W0 acceptance, and `docs/PRODUCT_LAYOUT.md`;
- all 26 current manifested files: A1–A15 and the ADR index, all eight contract modules, and both contract-test files;
- retained type/IR semantics needed to check the backend-neutral contract boundary.

The controlling digests matched:

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

At both the opening and closing review boundaries:

```sh
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST-2.sha256
```

reported all 26 entries `OK`. The manifest and controlling document hashes were unchanged at the end. The owned-tree inventory comparison produced no output, and no `__pycache__` directory was created.

The authorized focused suite passed:

```text
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.015s

OK
```

Pure in-memory Python 3.14 `-B` probes used the prescribed cached dependency and `src` paths. They wrote no files or bytecode and contacted no database, worker, service or repository.

The stopped authority counterexample produced:

```text
handle slots ('__weakref__',) dict False repr TrustedContext(<opaque identity>)
copy RAISE TypeError TrustedContext cannot be copied
deepcopy RAISE TypeError TrustedContext cannot be deep-copied
pickle RAISE TypeError TrustedContext cannot be serialized
asdict RAISE TypeError asdict() should be called on dataclass instances
vars RAISE TypeError vars() argument must have __dict__ attribute
reinit RAISE TypeError issued only by RuntimeAuthority
counterfeit validate RAISE ContractRefusal ... authority_invalid ...
cross issuer RAISE ContractRefusal ... authority_invalid ...
```

The stopped worker-erasure and resolution attacks produced:

```text
commit finish_without_commit RAISE ValueError commit-requested work requires terminal resolution
retained after refused finish CloseOutcome(UNRESOLVED, (tx,))
wrong identity RAISE ValueError outcome belongs to another transaction
indeterminate CloseOutcome(UNRESOLVED, (tx,))
committed CloseOutcome(CLOSED, ())
```

The three initial replacement counterexamples produced:

```text
duplicate active RAISE ContractRefusal ... transaction_identity_conflict ...
terminal reuse RAISE ContractRefusal ... transaction_identity_conflict ...
nonquiescent empty CloseOutcome(NONQUIESCENT, ())
quiescent empty CloseOutcome(CLOSED, ())
```

Every malformed knowledge value tested—`"indeterminate"`, `"fabricated"`, `0`, `1`, `False`, `True`, and `object()`—raised `ValueError`. A bypass-constructed malformed `CommitOutcome` also raised before mutation, leaving the fence unresolved and `_resolved` empty.

The additional cross-method probe supporting P3 produced:

```text
finish_without_commit after known commit RETURN None
terminal record after misuse CommitOutcome(KNOWN_COMMITTED, tx, revision)
```

---

## 1. Findings

### [P3-1] Terminal idempotency bypasses `finish_without_commit`’s pre-commit/known-abort precondition

**Classification:** bounded lifecycle-validation and diagnosability defect; **not a NEW ARCHITECTURAL root cause**.

**Location:** `src/garns/backends/contracts/state.py:272-303`, specifically `finish_without_commit()` at lines 272–277 and `_resolve_terminal()` at lines 285–303. The terminal-record lookup and identical-outcome return at lines 290–294 occur before the pre-commit `KNOWN_ABORTED` check at lines 299–300. The case is absent from `tests/contracts/test_contracts.py:389-543`.

**Violated invariant:** A8 states that pre-commit work may leave containment only with matching authoritative abort evidence. The method’s own contract says it finishes only pre-commit work with a matching authoritative abort. A caller invoking that method for a transaction already resolved as committed has used the wrong lifecycle operation and must not receive apparent success.

**Reproduction:**

```python
fence.begin(tx)
fence.request_commit(tx)
committed = CommitOutcome(
    CommitKnowledge.KNOWN_COMMITTED,
    tx,
    RevisionCursor(tx.scope, 1, 7),
)
fence.resolve(tx, committed)
fence.finish_without_commit(tx, committed)  # returns None
```

`_resolved[tx]` matches the supplied outcome, so `_resolve_terminal()` returns before checking that `require_commit_request=False` admits only `KNOWN_ABORTED`. Fence state remains correctly committed, but the illegal method call is accepted.

**Impact:** A conforming adapter can route a committed operation through the “without commit” completion API without detecting its lifecycle error. The retained terminal record prevents false closure or data loss in this reference model, so this is not a P2 safety failure; the concrete consequence is loss of fail-fast diagnostics at an exact shutdown/reconciliation boundary.

**Required correction:** In `_resolve_terminal()`, enforce operation-specific preconditions before the prior-terminal idempotency return. For `finish_without_commit()`, require exact `KNOWN_ABORTED` and reject transactions whose terminal record proves `KNOWN_COMMITTED`. Repeated identical known-abort completion may remain idempotent if that behavior is desired and documented. Do not weaken repeated `resolve()` idempotency for the original terminal operation.

**Closure/regression test:** Resolve a commit-requested identity as `KNOWN_COMMITTED`, then assert that `finish_without_commit(tx, committed)` and `finish_without_commit(tx, known_aborted)` both refuse without altering the retained committed outcome. Separately verify that repeated identical `resolve(tx, committed)` succeeds and conflicting resolution refuses. If repeated pre-commit abort completion is supported, test it explicitly.

---

## 2. Invariant analysis

The following attacks failed to produce blocking findings:

- **Duplicate identity admission:** active and terminal identities are rejected before `_begun` mutation. Set/dictionary collapse can no longer hide a second admitted command.
- **Qualified identity separation:** equal client IDs in different world/deployment scopes remain distinct and are independently accounted.
- **Resolution idempotency:** repeated identical resolution for the original operation returns without reopening work; conflicting resolution refuses.
- **Closed commit grammar:** exact `CommitKnowledge` membership is required. Known commit requires a same-scope revision; abort and indeterminate prohibit revisions. Bypass-created malformed instances are revalidated before mutation.
- **Close-result totality:** `NONQUIESCENT` accepts zero or more pending identities; `UNRESOLVED` requires nonempty pending identities; `CLOSED` forbids them. Quiescence and transaction knowledge are no longer conflated.
- **Original commit-erasure trace:** active commit-requested work cannot use `finish_without_commit()`. Indeterminate and wrong-identity results preserve containment; only matching terminal knowledge clears it.
- **Caller-handle containment:** the live handle has no ordinary path to claim data, issuer state or registry ownership. Exact registered identity remains necessary.
- **Authority validity:** runtime-owned clock, epoch and genuine task identity remain provider-sourced at trusted setup; wrong owner, expiry, invalidation, scope and capability refuse.
- **Detached claims:** mutable source capability containers and hostile string subclasses are normalized into immutable issuer-owned claims.
- **Subscription call graph:** one concrete authority-bound iterator validates before its awaited read and again before delivery. Renewal closes the old iterator; no authority-free parallel iterator protocol remains.
- **Cancellation grammar:** phase and evidence remain a closed relation. Commit-requested cancellation and acknowledgement loss remain indeterminate; invalid pairs refuse.
- **Publication compatibility:** qualified identity plus digest remains idempotent, conflict-detecting and retained across generation/compaction.
- **Migration coupling:** metadata-only and data-changing success remain disjoint; data-changing success requires matching request, binding, scope, generation, transaction identity, digest and nonempty effects.
- **Immutable values and plan binding:** parameter, row, delivery, mutation and ledger structures detach supported nested data; opaque plans retain qualified origin and authored-binding checks.
- **Protocol coherence:** query, snapshot, governed mutation, commit/reconciliation, schema inspection, migration, ledger replay, subscription binding and explicit close operations remain represented on the shared async surface. Unsupported capabilities remain explicit pre-effect refusals.
- **Language preservation:** no reviewed change reinterprets `query`, `question`, bounded live behavior, or the standalone `unenforced` flag.
- **Conditional-boundary hygiene:** no conditional compilation attributes were introduced or moved in the reviewed Python tuple; the C-style bracing rule is not applicable.

The explicitly deferred outcomes remain deferred: external capture W6/P6, cryptography/providers, arbitrary host-memory secrecy, actual worker/backend/database implementations and fault cuts, W2 exhaustive algebra, and W3 public naming/Surface. Nothing in this GO treats those outcomes as implemented or evidenced.

---

## 3. Risks and next action

The remaining material limitation is evidentiary: these are pure contracts, reference models and conforming fakes. They do not prove real thread containment, restart durability, PostgreSQL or SQLite execution, driver cancellation, migration atomicity, live-delivery durability, or database fault-cut behavior.

P3-1 should be corrected with its focused regression before or during the next implementation package, without reopening the registry/containment architecture. It does not block Code-axis acceptance of this exact replacement tuple. The next gate action implied by this verdict is lane-owner synthesis with the independent State-axis verdict on the same manifest; W1 may be accepted only if that verdict is also GO.
