# Garns v9-6 W1 corrected architecture package — STATE-AXIS REVIEW, ROUND 3

**Review object:** all 26 files in `dev-docs/W1-MANIFEST-3.sha256`, manifest SHA-256 `3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`; corrected remediation-round-2 package; controlling draft `dev-docs/W1-DRAFT-3.md`, SHA-256 `6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; controlling implementation plan SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; execution brief SHA-256 `1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`  
**Date:** 2026-10-03  
**Axis:** durable-state semantics and adversity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — all four round-2 State findings and the other six original State findings remain closed, but original State P2-7 is not fully closed: the executable SQLite worker fence can discard a commit-requested transaction and report `CLOSED` without a final durable outcome. This is a bounded reference-model correction, not a new architectural root cause. I pre-commit to GO on a revision that resolves P2-1 exactly as specified and introduces no new blocking defect.

---

## Prior-finding closure table

| ID | Disposition claimed | Independently re-run or re-traced on manifest 3 | Status |
|---|---|---|---|
| State-1 P2-1 | Replace cancellation timing with a closed phase/evidence grammar | Re-ran queued/not-started, statement, writes-applied, rollback-requested with confirmation or acknowledgement loss, connection loss, cleanup timeout, and commit-requested combinations. Only queued/not-started and rollback-requested/rollback-confirmed establish `KNOWN_ABORTED`; unresolved accepted pairs remain `INDETERMINATE`; incompatible pairs refuse. | CLOSED |
| State-1 P2-2 | Make qualified transaction publication idempotent and conflict-detecting across acknowledgement loss, generation and retention | Same qualified identity and digest returns its original revision without advancing; conflicting reuse refuses; the identity result survives generation change and compaction. | CLOSED |
| State-1 P2-3 | Require exact live issued context identity and prevent copied/reconstructed authority | Copy, deepcopy, replacement, serialization and counterfeit reconstruction refuse or fail registry validation; exact registered instance identity is required. | CLOSED |
| State-1 P2-4 | Defensively normalize immutable claims | Caller-owned capability sets are detached into `frozenset`; identity strings, scope, validity and epoch are normalized and validated. | CLOSED |
| State-1 P2-5 | Carry trusted authority through every protected operation | Ordinary open/acquire/release, execute/snapshot, transaction operations, schema/migration operations, ledger replay and subscription binding carry opaque context. Runtime validation rejects wrong task, clock expiry, epoch mismatch, scope mismatch and missing capability before fake invocation. | CLOSED |
| State-1 P2-6 | Recursively freeze contract values | Parameters, snapshots, deliveries, mutation identities/values and ledger effects detach supported nested containers and reject unsupported custom mutable values. | CLOSED |
| State-1 P2-7 | Fence late SQLite commit and retain unresolved containment until final outcome | Late commit request after shutdown refuses and nonquiescent close initially names unresolved transactions. The original “late worker can cross the fence” trace is closed. However, a commit-requested transaction can subsequently be erased through `finish_without_commit()` and close can claim `CLOSED` without reconciliation. The original final-outcome requirement is therefore not fully closed; see P2-1. | **OPEN** |
| State-2 P2-1 | Move clock, epoch and task ownership into runtime-owned providers | Protocol signatures expose no caller-selected `now`, epoch or owner token. `RuntimeAuthority` obtains all three from providers installed at trusted setup. Advancing any provider invalidates the context independently of operation arguments. | CLOSED |
| State-2 P2-2 | Couple migration success to the exact request and publication | Metadata-only success requires a proof digest and forbids a data publication. Backfill/DDL success requires nonempty typed effects, the exact next binding, matching scope/generation, migration transaction identity and payload digest. Refused and indeterminate results are distinct non-success types. | CLOSED |
| State-2 P2-3 | Make the cancellation phase/evidence product exhaustive | Re-ran the complete `OperationPhase × AbortEvidence` product. Invalid combinations, including commit-requested/rollback-confirmed, raise instead of manufacturing abort. Durable terminal evidence is handled through identity-bound reconciliation. | CLOSED |
| State-2 P2-4 | Capture genuine task identity and compare by identity | Equal-but-distinct hostile objects and real child tasks refuse. Nested/concurrent use still refuses, while the captured task can re-enter after leaving. | CLOSED |

## Changed-range analysis

Historical source bytes are not retained, so I did not invent a textual Git diff. I compared the initial and round-2 reports, both consolidated remediation plans, the prior manifests and current manifest, and the current 26 files.

The round-3 tuple changes the shared authority, subscription, migration, cancellation and transaction-owner surfaces identified by `W1-RemPlan-2.md`. The corrected implementation now has:

- a runtime-owned clock, invalidation epoch and actual-task provider;
- a non-iterable subscription that returns one concrete authority-bound iterator;
- validation both before and after an awaited delivery read;
- stale-iterator closure during renewal;
- request-coupled migration success and separate typed non-success;
- an explicit closed cancellation phase/evidence relation;
- owner capture and comparison by identity.

Those changed ranges close all four round-2 State findings. All original State protections also survive except the full closure of the SQLite worker-fence finding. The defect reported below is in the retained `WorkerCommitFence` completion path. It is not a third architectural root cause: the ADR architecture already requires containment until reconciliation and permits terminal close only after final outcomes. The executable model simply lacks the state validation and identity-bound terminal-resolution operation needed to enforce that existing design.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md` and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- the controlling implementation plan, provider-neutral seam and acceptance, D6a/D7/D8 and D4/D6b decisions, governed-write amendment and acceptance, W1 execution brief, W0 acceptance and `docs/PRODUCT_LAYOUT.md`;
- both original W1 reports, `W1-RemPlan.md`, both filed round-2 reports and `W1-RemPlan-2.md`;
- `W1-DRAFT-3.md`;
- all 26 manifest files: all A1–A15 ADRs and their index, all eight contract modules, and both contract-test files;
- retained inherited type semantics used by the contract adapter.

Start and end checks both produced the expected controlling hashes:

```text
3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13  dev-docs/W1-MANIFEST-3.sha256
6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566  dev-docs/W1-DRAFT-3.md
11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md
b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md
079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md
94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md
d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md
dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md
1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344  dev-docs/GarnsV9-6-W1-ExecutionBrief.md
13d77cf3820c3a61dc9905467cb332329ed374917e57a1db4bc64371092a2bbb  dev-docs/W1-RemPlan.md
ecd13b9b63981e9ad66bdaa83a141760c63544be1639380dc8a823fd09dafa83  dev-docs/W1-RemPlan-2.md
```

At both boundaries:

```text
shasum -a 256 -c dev-docs/W1-MANIFEST-3.sha256
```

reported `OK` for every one of the 26 entries. Comparing:

```text
rg --files docs/adr src/garns/backends/contracts tests/contracts
```

against the manifest produced no missing or unlisted file.

The prescribed suite passed:

```text
..................................
----------------------------------------------------------------------
Ran 34 tests in 0.010s

OK
```

I ran the worker-fence counterexample using the permitted pure in-memory Python environment. It produced:

```text
before CloseOutcome(knowledge=<CloseKnowledge.UNRESOLVED: 'unresolved'>,
                    unresolved=(TransactionIdentity(..., client_id='tx'),))
after CloseOutcome(knowledge=<CloseKnowledge.CLOSED: 'closed'>, unresolved=())
closed_without_reconcile True
```

No files, bytecode, services, databases, repositories or workspace state were modified.

---

## 1. Findings

### [P2-1] The SQLite shutdown fence can erase commit-requested work and report `CLOSED` without a final outcome

**Classification:** bounded state/reference-model correction; **not a new architectural root cause**. It is incomplete closure of original State P2-7.

**Location:** `src/garns/backends/contracts/state.py:213-244`, especially `request_commit()` at lines 226-231, `close_outcome()` at lines 236-240 and `finish_without_commit()` at lines 242-244; `tests/contracts/test_contracts.py:356-372`; contradicted by `docs/adr/A8-sqlite-async.md:11-18`, `docs/adr/A3-async-lifecycle.md:9-14`, and the lifecycle diagram in `docs/adr/README.md`.

**Violated invariant:** work that requested commit before the shutdown fence remains durably reconcilable. Terminal `CLOSED` requires quiescence and a final identity-bound outcome; cleanup may not discard an indeterminate transaction merely by asserting that it finished without commit.

**Reproduction/state sequence:**

1. Create `WorkerCommitFence`.
2. `begin(tx)`.
3. `request_commit(tx)` before shutdown; the database commit may now become durable even if its acknowledgement is lost.
4. `start_shutdown()`.
5. `close_outcome(False)` correctly returns `UNRESOLVED(tx)`.
6. Call the model’s only completion operation, `finish_without_commit(tx)`.
7. `finish_without_commit()` unconditionally removes `tx` from both `_begun` and `_commit_requested`.
8. `close_outcome(True)` now returns `CLOSED`.

No authoritative rollback evidence, durable committed row, durable abort record or `reconcile(tx, ...)` result was supplied. The model does not provide a commit/reconciliation completion operation, nor does `finish_without_commit()` reject a transaction that had crossed `request_commit()`.

**Impact:** the executable W1 model permits containment and reconciliation ownership to disappear after acknowledgement loss. A conforming SQLite shutdown implementation modeled on this transition can claim terminal closure while a commit-requested transaction is committed or still indeterminate, losing the identity needed for cleanup/reconciliation and allowing callers to act on a false final state.

**Required correction:** make worker completion phase-aware and outcome-bound.

- `finish_without_commit(tx)` must refuse when `tx` is in `_commit_requested` unless authoritative identity-bound abort/rollback evidence is supplied.
- Add an explicit resolution transition for commit-requested work that consumes a matching terminal `CommitOutcome` or equivalent durable reconciliation result for the same transaction.
- `KNOWN_COMMITTED` and `KNOWN_ABORTED` may clear containment; `INDETERMINATE` must remain in `_begun`/unresolved ownership.
- Reject resolution for another transaction identity.
- `close_outcome()` may return `CLOSED` only after every begun or commit-requested identity has a final outcome.

This does not require redesigning the worker-fence architecture; it makes the reference state machine enforce the architecture already stated by A3/A7/A8.

**Closure/regression test:** exercise at least these traces:

1. begun, never commit-requested, authoritative no-effect completion → may clear and close;
2. begun, commit-requested, `finish_without_commit()` → must refuse and remain `UNRESOLVED`;
3. begun, commit-requested, matching `INDETERMINATE` result → remains `UNRESOLVED`;
4. begun, commit-requested, matching `KNOWN_COMMITTED` result → clears and may close;
5. begun, commit-requested, matching authoritative `KNOWN_ABORTED` result → clears and may close;
6. result for a different qualified transaction identity → refuses without changing containment;
7. acknowledgement loss followed by restart/reconciliation → preserves the identity until one of the two final results is established.

---

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Runtime-owned freshness:** ordinary protected method signatures expose no caller-selected time, epoch or owner. Advancing the injected runtime clock or epoch, invalidating the exact instance, or switching tasks makes validation fail.
- **Task ownership:** both hostile equality collisions and actual child-task use refuse by identity. Nested or overlapping transaction calls remain rejected.
- **Subscription delivery:** the subscription is not directly iterable and offers no parallel authority-free delivery method. Its concrete iterator validates before reading and after the await. Expiry, epoch change, child-task use and renewal/closure prevent delivery; the reader is not invoked when entry validation fails.
- **Migration outcome coupling:** metadata-only, backfill and DDL-data-change forms are exhaustive. Missing/empty publication, wrong scope, wrong generation, wrong transaction identity and wrong digest refuse. Non-success cannot masquerade as accounting success.
- **Cancellation:** timing is separate from evidence. Rollback acknowledgement loss, connection loss and cleanup timeout remain indeterminate. Commit-requested plus rollback confirmation is invalid rather than aborted. Durable abort/commit evidence enters through qualified reconciliation.
- **Publication identity:** qualified identity plus payload digest makes acknowledgement-loss repetition idempotent, conflicting reuse a typed refusal, and retains the original outcome across generation change and compaction.
- **Commit ordering:** revisions advance on the publication operation rather than request order. The ADR requires the real implementation to serialize publication immediately before commit under one per-scope durable lock.
- **Exact snapshot watermark:** snapshot and refresh prose require rows and high-water cursor from the same repeatable snapshot; delivery construction enforces common scope/generation and `previous < triggered_by <= observed_through`.
- **Immutable values:** parameters, snapshots, deliveries, mutations and ledger effects recursively detach supported nested values.
- **Recovery grammar:** generation mismatch and below-floor replay return typed refetch rather than translation. Compaction advances the durable floor before deleting strictly older payload, while transaction reconciliation identities remain outside compaction.
- **Binding fidelity:** plans retain qualified world/deployment, IR digest, authored-storage digest and generation; wrong binding or generation refuses before fake adapter invocation.
- **Capability and implementation isolation:** the common protocols retain required operations for both backend descriptions; unsupported capabilities refuse explicitly. Contract modules contain no driver, SQL text, schema-case dispatch, expected-answer dispatch or compiler-node algebra.
- **Preserved language semantics:** the package does not reinterpret `query`, `question`, bounded live questions or standalone `unenforced`.
- **Deferred evidence:** external capture, named providers, W2 exhaustive algebra, W3 public surface/runtime and W4–W5 database/live proofs remain correctly deferred. The pure models and fakes were not mistaken for real PostgreSQL, SQLite-worker, migration-atomicity or fault-cut evidence.

The unused `AbortEvidence.AUTHORITATIVE_ABORT_RECORD` member is rejected by the cancellation product because A7 routes durable abort evidence through identity-bound reconciliation. I did not elevate this to a separate finding: the accepted relation is closed and fail-closed, though removing or documenting that cancellation-inapplicable member would reduce implementation ambiguity.

---

## 3. Risks and next action

The 34 passing tests do not exercise removal of a transaction after commit authorization. The suite checks that an already commit-requested transaction initially remains unresolved, but it never calls `finish_without_commit()` on that same transaction or requires a final identity-bound result before terminal close.

The single next action is a bounded correction to `WorkerCommitFence` and its regressions as specified in P2-1, followed by focused State re-verdict on a newly pinned tuple. This finding does not trigger the architectural two-remediation cap because it neither changes nor discovers a new architecture: it enforces A3/A7/A8’s existing containment-until-final-outcome design. Any attempted correction that changes that architecture, or any newly discovered architectural root, must stop the lane for operator redesign-or-accept rather than begin another architectural remediation.
