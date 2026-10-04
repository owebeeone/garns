# W1 Registry/Containment Redesign — CODE-AXIS REVIEW, ROUND 3

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST-3.sha256`, manifest SHA-256 `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`; bounded replacement-object remediation 2; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT-3.md`, SHA-256 `458aeea7dd184a96af413d2550b6dffb54ced623a6a4cd406468e94f461c6128`; source writes stopped  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; remediation plan `dev-docs/W1-RegistryContainmentRedesign-RemPlan-2.md`, SHA-256 `f96ae011016e382c53d439311275b7f1c9e6f6ca5c62bef4f0423e23c269c2ed`; sources read directly from the hash-pinned working tree  
**Date:** 2026-10-03  
**Axis:** focused Code-axis unchanged-GO and changed-range re-verdict: architecture, interfaces, call graphs, compatibility, and preservation of previously verified closures. Independent, adversarial, read-only. The other axis runs separately; nothing here relies on its current-round report. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, or P2 Code findings. The two-file correction is contained, preserves every prior closure, and introduces no interface, result-algebra, call-graph, or architectural change. Previously reported Code P3-1 remains truthfully present and is explicitly deferred to W3 by the merged plan.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Round-2 State P2-1 | Require exact cancellation phase/evidence and reconciliation finding members; reject revisions on aborted or unresolved reconciliation | `cancellation_outcome()` now rejects raw strings, integers, booleans, arbitrary objects, and matching foreign enum members before relation lookup. `reconcile()` applies the same exact-member guard. Committed reconciliation still requires a same-scope revision; aborted and unresolved findings now reject any revision. The original raw-string manufactured-abort path refuses while the worker identity remains contained. | **CLOSED for Code-axis compatibility/call-graph purposes** |
| Round-2 Code P3-1 | Record as nonblocking follow-up and defer method-specific terminal-fast-path validation to W3; do not patch opportunistically here | The relevant `WorkerCommitFence.finish_without_commit()` and `_resolve_terminal()` logic is unchanged apart from shifted line numbers. After a known commit, `finish_without_commit(tx, same_committed_outcome)` still returns `None` without altering terminal truth. This exactly matches the accepted deferral; it was neither silently fixed nor worsened. | **DEFERRED TO W3, NONBLOCKING** |
| Initial replacement Code P2-1 | Reject duplicate active admission and terminal identity reuse | Active and terminal reuse still raise `TRANSACTION_IDENTITY_CONFLICT`; repeated resolution remains idempotent and conflicting resolution refuses. | **CLOSED, PRESERVED** |
| Initial replacement State P2-1 | Enforce exact closed `CommitOutcome` knowledge and revision grammar | Malformed terminal knowledge still refuses at construction and is independently rejected at resolution before mutation. Known commit requires a same-scope revision; abort and indeterminate prohibit revisions. | **CLOSED, PRESERVED** |
| Initial replacement State P2-2 | Separate worker quiescence from transaction knowledge | Nonquiescent close with zero pending identities still returns `NONQUIESCENT`; quiescent empty close returns `CLOSED`; pending quiescent work returns `UNRESOLVED`. | **CLOSED, PRESERVED** |
| Stopped W1 Code-3 P2-1 / initial Code P2-5 | Keep authority claims solely in issuer registry state behind an identity-only handle | `authority.py` and A11 are byte-identical to the previously reviewed GO tuple. The empty-handle, exact-issued-instance, cross-issuer, copy/serialization, runtime-owned clock/epoch/task, and post-await validation protections are unchanged. | **CLOSED, PRESERVED** |
| Stopped W1 State-3 P2-1 / initial State P2-7 | Retain commit-requested work until identity-matching terminal resolution | Active `finish_without_commit()` still refuses commit-requested work; malformed or wrong-identity resolution leaves it contained; indeterminate remains unresolved; matching terminal resolution clears it. | **CLOSED, PRESERVED** |

## Changed-range analysis

Comparison of the round-2 and round-3 checksum inventories shows exactly two changed paths:

```text
src/garns/backends/contracts/state.py
  2bb7dcffc1066d07e9d68c985067273bfb9b359748ec10063fd80abf78237a2a
  febfb507dfa079dd2803407eeb1425d09fb61f792ef8d23b6a6052f229fd5802

tests/contracts/test_contracts.py
  df959140aa2b61966920a74f9d744c5e3a78ccf850a12eb47f24e984b0f1c441
  d88c21c2ad7a282d751bfe2ab35ea566ae568996e31843c3bd9d934d0b15bb7f
```

All other 24 manifested files are byte-identical to the round-2 Code-GO tuple. The complete inventory under `docs/adr`, `src/garns/backends/contracts`, and `tests/contracts` exactly matches the 26 manifest paths.

The production-code delta is confined to:

- exact `OperationPhase` and `AbortEvidence` guards at `src/garns/backends/contracts/state.py:127-130`;
- an exact `ReconcileFinding` guard at `state.py:158-161`;
- explicit revision refusal for aborted reconciliation at `state.py:166-169`, complementing the existing unresolved-revision refusal.

The matching tests enumerate valid members and reject raw strings, integers, booleans, arbitrary objects, and foreign enums; they also cover missing/wrong-scope committed revisions and prohibited aborted/unresolved revisions.

The changes do not modify exported names, parameters, return unions, close knowledge, commit knowledge, worker state representation, protocol methods, authority representation, ADRs, backend behavior, or call-graph ownership. No **NEW ARCHITECTURAL root cause** was found.

---

## 0. Evidence base

I read and checked:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, and the updated `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical report requirements retained from the preceding review;
- full `W1-RegistryContainmentRedesign-RemPlan-2.md` and `W1-RegistryContainmentRedesign-DRAFT-3.md`;
- the complete current `state.py` and the relevant complete state-model test region;
- both round-2 and round-3 manifest inventories;
- the unchanged integrated tuple and controlling documents previously read for the round-2 Code review;
- the previous Code P3 counterexample and all registry/containment closure paths affected by the state helper.

At both review boundaries:

```sh
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST-3.sha256
```

reported all 26 entries `OK`.

The opening and closing controlling hashes matched:

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

Manifest-to-owned-inventory comparison produced no missing or extra paths. No `__pycache__` directory was created.

The authorized focused suite passed:

```text
.............................................
----------------------------------------------------------------------
Ran 45 tests in 0.013s

OK
```

Pure in-memory Python 3.14 `-B` probes used the prescribed cached dependency and `src` path. They wrote no files or bytecode and contacted no database, worker, service, repository, or peer report.

The corrected malformed-input attacks produced:

```text
raw cancellation abort RAISE ValueError cancellation requires declared phase and evidence members
foreign cancellation abort RAISE ValueError cancellation requires declared phase and evidence members
raw attacks retain CloseOutcome(UNRESOLVED, (tx,))

reconcile malformed 'aborted' RAISE ValueError reconciliation requires a declared finding member
reconcile malformed 0 RAISE ValueError reconciliation requires a declared finding member
reconcile malformed 1 RAISE ValueError reconciliation requires a declared finding member
reconcile malformed False RAISE ValueError reconciliation requires a declared finding member
reconcile malformed True RAISE ValueError reconciliation requires a declared finding member
reconcile malformed object RAISE ValueError reconciliation requires a declared finding member
reconcile malformed Foreign.ABORTED RAISE ValueError reconciliation requires a declared finding member
```

Revision-relation probes produced:

```text
revision prohibited aborted RAISE ValueError aborted reconciliation cannot carry a revision
revision prohibited still_in_flight RAISE ValueError unresolved reconciliation cannot carry a revision
revision prohibited not_found_not_final RAISE ValueError unresolved reconciliation cannot carry a revision
valid abort CommitOutcome(KNOWN_ABORTED, tx, None)
valid commit CommitOutcome(KNOWN_COMMITTED, tx, same-scope revision)
valid missing CommitOutcome(INDETERMINATE, tx, None)
```

Preserved-closure probes produced:

```text
duplicate active RAISE ContractRefusal ... transaction_identity_conflict ...
malformed terminal RAISE ValueError commit knowledge must be a declared CommitKnowledge member
still unresolved CloseOutcome(UNRESOLVED, (tx,))
terminal reuse RAISE ContractRefusal ... transaction_identity_conflict ...
nonquiescent empty CloseOutcome(NONQUIESCENT, ())
active finish RAISE ValueError commit-requested work requires terminal resolution
```

The accepted P3 deferral was checked explicitly:

```text
P3 unchanged wrong finish after known commit RETURN None
```

The retained committed outcome was not altered.

## 2. Invariant analysis

The corrected helper boundary now holds:

- Exact enum provenance is required before cancellation or reconciliation branching.
- String-valued enum equality can no longer let raw or foreign members enter the closed state grammar.
- Malformed cancellation input cannot manufacture `KNOWN_ABORTED` for a later fence completion.
- Reconciliation cannot attach a revision to abort or unresolved knowledge.
- Valid declared cancellation pairs retain their prior results.
- Valid committed reconciliation retains the same-scope revision requirement.
- `STILL_IN_FLIGHT` and `NOT_FOUND_NOT_FINAL` remain indeterminate rather than manufacturing abort.

Previously accepted architecture remains intact:

- Duplicate and terminal worker identity reuse refuse before admission.
- Qualified identities with equal client components remain scope-distinct.
- Commit outcomes are exact and independently revalidated before containment mutation.
- Worker quiescence and transaction knowledge remain independent dimensions.
- Commit-requested work cannot disappear through the active pre-commit completion route.
- The caller-held trusted context remains an empty identity handle with registry-owned claims and genuine task ownership.
- Runtime-owned clock, epoch, scope, capability, invalidation, and pre/post-await delivery validation remain unchanged.
- Cancellation timing remains separate from authoritative terminal knowledge.
- Publication idempotency, migration coupling, immutable value boundaries, plan binding, async protocol inventory, and explicit capability refusal are unaffected.
- No conditional compilation or C-style control-flow rule is implicated by the two-file Python change.

Code P3-1 remains bounded and accurately documented. Its reproduction still succeeds only after terminal truth has already been retained; it neither changes the known-committed outcome nor reopens or drops containment. Deferring method-specific wrong-operation diagnostics to W3 is therefore consistent with its nonblocking classification.

Explicit deferrals remain deferrals: external capture W6/P6, cryptographic/provider integration, arbitrary host-memory secrecy, actual backend/worker/database implementation and fault cuts, W2 exhaustive algebra, and W3 public names/Surface and reference-model integration. This review does not treat any of those outcomes as implemented.

## 3. Risks and next action

The remaining Code-axis risk is the already recorded P3 lifecycle diagnostic: the terminal idempotency fast path can accept the wrong completion method after a known commit. The merged plan assigns its method-specific correction and regression to W3, and this round correctly did not disguise that follow-up as part of the bounded State fix.

Pure reference models and passing tests still do not establish real worker containment, restart durability, database execution, cancellation, migration atomicity, or fault-cut recovery.

The single next action is lane-owner synthesis with the focused State-axis re-verdict on this exact 26-file tuple. If State also reports GO, the manager may accept the replacement W1 architecture while carrying Code P3-1 explicitly into W3; no additional W1 architecture correction is indicated by this Code review.
