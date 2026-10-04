# Garns v9-6 W1 registry/containment redesign — STATE-AXIS REVIEW

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256`, manifest SHA-256 `fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff`; operator-authorized W1 registry/containment replacement design; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT.md`, SHA-256 `d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; redesign brief SHA-256 `afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d`; controlling implementation plan SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`  
**Date:** 2026-10-03  
**Axis:** durable-state semantics and adversity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block acceptance. The two final stopped-W1 counterexamples are closed, and the preserved prior fixes survive, but the redesigned worker model accepts malformed outcome knowledge as terminal and has no valid close outcome for a nonquiescent worker with no unresolved transaction identities. P2-2 is a **NEW ARCHITECTURAL root cause** in the replacement object’s close-state algebra. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified and introduces no new blocking defect.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on redesigned tuple | Status |
|---|---|---|---|
| Code-3 P2-1 / initial Code P2-5 | Replace the caller-held claims object with an empty identity-only handle; retain claims and task ownership solely in the issuer registry | `TrustedContext` has only `__weakref__`, no claim/issuer/registry field or back-reference. Direct attribute access and mutation, reinitialization, copy, deepcopy, pickle/reduction, `vars`, dataclass conversion, counterfeit construction and cross-issuer validation were retried. Claims remain detached in the issuing `RuntimeAuthority`; only the exact registered live instance validates. | CLOSED |
| State-3 P2-1 / initial State P2-7 | Prevent commit-requested identities from leaving containment without an identity-matching terminal result | `finish_without_commit()` now rejects commit-requested work. Wrong identity refuses without mutation; `INDETERMINATE` remains unresolved; matching `KNOWN_COMMITTED` and `KNOWN_ABORTED` clear containment; identical terminal resolution repeats idempotently and conflicting resolution refuses. The original finish-then-false-close trace no longer succeeds. | CLOSED |
| State-1 P2-1 / State-2 P2-3 | Closed cancellation phase/evidence grammar | The enumerated `OperationPhase × AbortEvidence` relation remains fail-closed: only queued/not-started and rollback-requested/rollback-confirmed establish abort; commit-requested cancellation remains indeterminate; incompatible pairs refuse. | CLOSED |
| State-1 P2-2 | Qualified, idempotent and conflict-detecting publication | Qualified transaction identity plus payload digest still returns the original revision on repetition, rejects conflicting reuse and survives generation/retention changes. | CLOSED |
| State-1 P2-3 / State-2 P2-1 / State-2 P2-4 | Genuine runtime-owned context, clock, epoch and task ownership | Exact registered context identity remains required. Clock, epoch and actual task identity come from trusted providers; wrong task, expiry, invalidation, scope or capability refuses. | CLOSED |
| State-1 P2-4 | Detached normalized claims | Mutable capability inputs and hostile string subclasses remain normalized into immutable registry-owned values. | CLOSED |
| State-1 P2-5 | Authority at every protected boundary | Protocol and conforming-fake paths retain context validation before backend effects, including post-await subscription validation. | CLOSED |
| State-1 P2-6 | Recursive immutable contract values | Parameters, snapshots, deliveries, mutations and ledger effects still detach supported nested containers and reject unsupported custom values. | CLOSED |
| State-2 P2-2 | Migration outcome tied to exact request and publication | Metadata-only and data-changing success remain disjoint; data-changing success requires matching binding, scope, generation, transaction identity, digest and nonempty effects. | CLOSED |
| Round-2 Code P2-1 | One authority-bound subscription delivery graph | The subscription still exposes one bound iterator; validation remains before and after awaited reads, and renewal closes the stale iterator. | CLOSED |

## Changed-range analysis

No historical source snapshot or Git diff exists, so no textual before/after diff was invented. I compared the two manifest checksum inventories. Their path sets are identical, and exactly these six authorized paths changed from `W1-MANIFEST-3.sha256`:

- `docs/adr/A11-trusted-context.md`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/authority.py`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

No unlisted path exists under `docs/adr`, `src/garns/backends/contracts` or `tests/contracts`.

The authority changes implement the authorized registry-only design without weakening the retained validation barriers. The worker changes close the stopped tuple’s unsafe `finish_without_commit()` trace by introducing outcome-bound resolution and retained terminal records.

P2-1 below is a bounded validation defect in that new resolution implementation.

P2-2 is a **NEW ARCHITECTURAL root cause**: the redesign retains a two-valued close-result algebra that equates “not closed” with “has unresolved transaction identities.” A non-killable worker can remain nonquiescent after all transaction identities are terminal, or before any transaction begins. That reachable state has no representation.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md` and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- `W1-RegistryContainmentRedesign-Brief.md`, `W1-STOP.md`, complete final `W1-ReviewCode-3.md` and `W1-ReviewState-3.md`;
- both W1 remediation plans, the W1 execution brief, W0 acceptance and `docs/PRODUCT_LAYOUT.md`;
- the accepted implementation plan, provider-neutral seam, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance;
- `W1-RegistryContainmentRedesign-DRAFT.md`;
- all 26 manifested files, including A1–A15 and the ADR index, all eight contract modules and both contract-test files;
- retained type/IR semantics used by the contract adapter.

The start and end digest checks matched the required tuple:

```text
fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff  dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256
d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd  dev-docs/W1-RegistryContainmentRedesign-DRAFT.md
afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d  dev-docs/W1-RegistryContainmentRedesign-Brief.md
11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md
b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md
079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md
94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md
d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md
dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md
1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344  dev-docs/GarnsV9-6-W1-ExecutionBrief.md
```

Both executions of:

```text
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256
```

reported `OK` for all 26 entries. Manifest-to-owned-inventory comparison produced no missing or extra paths.

The prescribed suite passed:

```text
.......................................
----------------------------------------------------------------------
Ran 39 tests in 0.010s

OK
```

The original final State counterexample was retried. Commit-requested `finish_without_commit()` and wrong-identity resolution both raised `ValueError`; indeterminate resolution retained the qualified identity; matching committed resolution allowed terminal close.

The malformed-outcome counterexample produced:

```text
malformed constructed CommitOutcome(knowledge='fabricated',
  transaction=TransactionIdentity(
    scope=QualifiedDeployment(world='W', deployment='D'),
    client_id='t'),
  revision=None)

malformed closes CloseOutcome(
  knowledge=<CloseKnowledge.CLOSED: 'closed'>,
  unresolved=())
```

The nonquiescent-empty counterexamples produced:

```text
never-begun ValueError unresolved close must name transactions
resolved-nonquiescent ValueError unresolved close must name transactions
```

All probes used Python 3.14 with `-B`, `PYTHONDONTWRITEBYTECODE=1`, the prescribed cached dependency and product `src`. No file, bytecode, service, database, repository or workspace state was modified.

---

## 1. Findings

### [P2-1] Commit resolution accepts malformed knowledge as a terminal outcome

**Classification:** bounded correctness correction; not a new architectural root.

**Location:** `src/garns/backends/contracts/state.py:68-78,252-275`, especially `CommitOutcome.__post_init__()` and `_resolve_terminal()`.

**Violated invariant:** only the closed final-outcome grammar—`KNOWN_COMMITTED` with a same-scope revision, `KNOWN_ABORTED` without one, or `INDETERMINATE` without one—may affect containment. Invalid or malformed outcome knowledge must refuse without changing state. Closed state must never be created from invented final knowledge.

**Reproduction/state sequence:**

1. Construct a `WorkerCommitFence`.
2. Begin transaction `tx`, request commit, and start shutdown.
3. Construct `CommitOutcome("fabricated", tx)`.
4. `CommitOutcome.__post_init__()` accepts it because `"fabricated" is not CommitKnowledge.KNOWN_COMMITTED` and no revision is present.
5. Call `resolve(tx, malformed)`.
6. `_resolve_terminal()` treats every knowledge value except the exact `INDETERMINATE` member as terminal. Because commit was requested, it does not require the exact `KNOWN_ABORTED` member.
7. It records the malformed result and removes `tx` from both containment sets.
8. `close_outcome(True)` returns `CLOSED`.

An arbitrary object or other non-enum value with no revision follows the same path.

**Impact:** malformed adapter, deserialization or implementation data can erase a commit-requested identity and produce terminal closure without known commit or known abort. This recreates the safety consequence of the stopped W1 finding through a different input: unresolved durable work can disappear from reconciliation ownership.

**Required correction:** validate and normalize `CommitOutcome.knowledge` at construction, requiring an exact `CommitKnowledge` member or an explicitly safe conversion that rejects unknown values. Enforce the complete knowledge/revision relation explicitly. `_resolve_terminal()` should independently admit only exact `KNOWN_COMMITTED` and `KNOWN_ABORTED` terminal members and retain exact `INDETERMINATE`; every other value must refuse before mutation.

**Closure/regression test:** enumerate every valid `CommitKnowledge` member and representative malformed values including unknown strings, integers, booleans and arbitrary objects. Verify malformed construction or resolution refuses, `_begun`, `_commit_requested` and `_resolved` remain unchanged, and close remains unresolved. Retain tests for known-commit revision requirements, known-abort revision prohibition, indeterminate retention and conflicting repeated resolution.

### [P2-2] The close-result algebra cannot represent a nonquiescent worker with no unresolved transaction identity

**Classification:** **NEW ARCHITECTURAL root cause** in the replacement object.

**Location:** `src/garns/backends/contracts/state.py:63-90,239-243`; contradicted by `docs/adr/A8-sqlite-async.md:21-25` and `docs/adr/README.md:73-76,97-102`.

**Violated invariant:** terminal `CLOSED` requires both worker quiescence and final outcomes for every begun transaction. Failure to quiesce must produce a typed nonterminal close state without inventing abort, dropping containment or falsely creating a transaction identity.

**Reproduction/state sequences:**

1. **No work begun:** create a fence, start shutdown, and call `close_outcome(False)`.
2. `_begun` is empty, so the method tries `CloseOutcome(UNRESOLVED, ())`.
3. `CloseOutcome.__post_init__()` rejects an unresolved result with no transaction identities.

The same failure occurs after a real transaction receives a valid terminal outcome and leaves `_begun`, while the worker thread is still nonquiescent:

1. Begin and request commit.
2. Resolve with matching `KNOWN_COMMITTED` or `KNOWN_ABORTED`.
3. The identity is correctly removed from transaction containment.
4. Call `close_outcome(False)` because the worker has not stopped.
5. The model again raises `ValueError`.

Returning `CLOSED` instead would violate the explicit quiescence condition. Retaining a resolved identity as “unresolved” would falsely erase final knowledge. Inventing a new transaction identity would also be invalid. The current two-state result therefore has no legal answer.

**Impact:** an ordinary empty-worker shutdown or a worker that lingers after transaction reconciliation cannot return the typed close outcome promised by A3/A8. Implementations following this algebra must either throw an unmodeled exception, falsely report closure, misreport a final transaction as unresolved, or invent an identity. This makes shutdown/retry behavior non-total and prevents callers from reliably retaining worker/connection containment until quiescence.

**Required correction:** extend the close-state grammar so worker quiescence and unresolved transaction knowledge are independent dimensions. For example, add an explicit typed `NONQUIESCENT`/`DRAINING` close knowledge that may carry zero or more unresolved transaction identities, while reserving `CLOSED` for quiescent state with none. Preserve qualified unresolved identities whenever they exist. Update A8 and the lifecycle diagram to state the exact exhaustive relation and caller obligations.

**Closure/regression test:** exhaustively test the product of:

- quiescent versus nonquiescent;
- zero versus one or multiple begun identities;
- pre-commit, commit-requested-indeterminate and terminally resolved identities.

Every reachable combination must produce one typed result without exception. `CLOSED` must occur only for quiescent state with no unresolved identities. Nonquiescent state with zero identities must remain explicitly nonterminal. Indeterminate identities must remain listed, and final identities must not be relabeled unresolved.

---

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Original authority-disclosure trace:** the caller-held context is now an empty identity handle. Its ordinary attributes, slots and diagnostics expose no claims or issuer reference. Copying, reduction, serialization, dataclass helpers, reconstruction and cross-issuer use do not create authority.
- **Original unsafe-finish trace:** commit-requested work cannot pass through `finish_without_commit()`. Matching indeterminate resolution retains it; matching final resolution clears it; wrong identity and wrong revision scope refuse without mutation.
- **Repeated/conflicting resolution:** identical terminal resolution is idempotent because `_resolved` retains the outcome; conflicting later resolution refuses.
- **Late commit fence:** shutdown prevents a begun-but-not-commit-requested command from crossing into commit authorization after the fence.
- **Runtime-owned freshness and ownership:** ordinary protected calls expose no caller-selected clock, epoch or task token. Exact task identity, expiry, epoch, scope, capability and explicit invalidation remain enforced.
- **Subscription delivery:** one bound iterator validates before reading and after the await. Expiry, epoch change, task change, invalidation, closure and renewal prevent stale delivery.
- **Cancellation evidence:** cancellation timing does not manufacture terminal database knowledge. Rollback acknowledgement loss, connection loss and cleanup timeout stay indeterminate; incompatible phase/evidence pairs refuse.
- **Publication identity and ordering:** qualified identity plus payload digest remains idempotent and conflict-detecting across generation and retention. Revision allocation follows publication order rather than request order.
- **Migration accounting:** successful data-changing migration remains tied to the exact request, binding, qualified transaction, generation, digest and nonempty effects; metadata-only success remains separate.
- **Snapshot/replay grammar:** delivery cursors require one scope and generation with `previous < triggered_by <= observed_through`; generation and retained-floor failures remain typed refetch paths.
- **Immutable state values:** accepted parameter, row, delivery, mutation and ledger structures detach supported nested inputs.
- **Binding and type fidelity:** retained `TypeRef` dimensions, result ownership, immutable plan bytes and authored binding/generation checks survive.
- **Capability parity:** both backend contracts retain the common operation surface and explicit pre-effect refusal for unsupported capability.
- **Language preservation:** no change to `query`, `question`, bounded live questions or standalone `unenforced` semantics was found.
- **Deferral discipline:** external capture, cryptographic/provider integration, arbitrary host-memory secrecy, actual backend/worker/database durability, W2 algebra and W3 public names remain deferred rather than falsely passed.

The reference model still accepts caller-constructible `KNOWN_ABORTED` and `KNOWN_COMMITTED` objects once their shape is valid. I did not report that alone as a separate finding: W1 models the typed boundary, while durable provenance is explicitly deferred to real reconciliation implementations. P2-1 is narrower and independently reproducible because the model accepts values outside even its declared closed grammar.

---

## 3. Risks and next action

The 39 passing tests cover the two stopped-W1 traces but omit malformed `CommitOutcome.knowledge` and both zero-identity/nonquiescent close states. Pure models remain contract-shape evidence only; they do not establish restart durability, real worker containment or database reconciliation.

The single next action is one consolidated replacement-object remediation for P2-1 and P2-2, with an explicit exhaustive outcome matrix and close-state product, followed by a newly pinned tuple and State re-review. Because P2-2 is a new architectural root, this consumes the redesign object’s first architectural remediation round; its ordinary two-round cap remains in force.
