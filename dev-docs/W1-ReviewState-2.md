# Corrected W1 Architecture Package, Remediation Round 1 — STATE-AXIS REVIEW

**Review object:** all 26 files pinned by `dev-docs/W1-MANIFEST-2.sha256`, aggregate SHA-256 `3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6`, with controlling draft `dev-docs/W1-DRAFT-2.md` SHA-256 `d78c83ddcce4e1660bed3ab3e36b3b473b05c5e28d0fc2c638479abc4a9b4569`; proposed W1 remediation-round-1 package reviewed 2026-10-03.  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`; files read directly from the SHA-pinned, pre-initial-commit tuple authorized by accepted-plan §15. No clean-commit or landing claim.  
**Date:** 2026-10-03  
**Axis:** durable-state semantics and adversity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — four P2 findings block. Two are **NEW ARCHITECTURAL** roots: caller-supplied authority freshness and migration outcomes that do not prove their asserted atomic accounting. I pre-commit to GO on a revision that resolves P2-1 through P2-4 as specified and preserves the verified prior-finding closures below.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| State P2-1 | Replace cancellation’s `commit_requested` shortcut with phase/evidence grammar; unresolved rollback remains indeterminate. | Re-ran statement, writes-applied, rollback-ack-loss, connection-loss, cleanup-timeout and commit-requested traces. All unresolved cases now return `INDETERMINATE`; queued/not-started and rollback-requested/rollback-confirmed return `KNOWN_ABORTED`. The original counterexample is closed. P2-3 below is a different malformed phase/evidence combination admitted by the new grammar. | CLOSED |
| State P2-2 | Qualified identity-to-revision publication with idempotence and conflict detection across acknowledgement loss, generations and compaction. | Publishing the same qualified identity and payload returns the original revision without advancing; a conflicting payload refuses. The recorded identity result survives `change_generation()` and `compact_to()`. Cross-scope reconciliation remains rejected. | CLOSED |
| State P2-3 | Runtime-owned exact-instance provenance; copies, reconstruction and serialization cannot preserve authority. | `copy.copy`, `copy.deepcopy`, `dataclasses.replace` and pickle all raise `TypeError`; `object.__new__(TrustedContext)` fails registry validation; direct claim reassignment/deletion refuses. | CLOSED |
| State P2-4 | Defensive normalization and validation of claims. | Mutating the source capability set after claim construction does not change the stored `frozenset`; hostile string subclasses normalize to plain strings; empty capabilities, infinite validity and invalid epochs refuse. | CLOSED |
| State P2-5 | Carry authority through ordinary open/acquire/execute/snapshot and all protected operations. | Protocols and conforming fake now require a `TrustedContext`; counterfeit, wrong-owner, expired, wrong-epoch, wrong-scope and insufficient-capability cases refuse before fake adapter invocation. The original missing-path counterexample is closed. P2-1 below is a new authority-source root: freshness inputs themselves remain caller-controlled. | CLOSED |
| State P2-6 | Recursively immutable parameter, snapshot, delivery, mutation and ledger values. | Nested lists, mappings and sets are detached into immutable tuples, `FrozenMap` and `frozenset`; mutation of the original graph does not change snapshots or deliveries; unsupported custom objects refuse. | CLOSED |
| State P2-7 | Executable SQLite commit fence and typed unresolved close retaining containment/reconciliation ownership. | A transaction begun before shutdown but not yet commit-requested cannot request commit after the fence; nonquiescent close reports `UNRESOLVED` with the transaction identity; already-requested commit remains indeterminate rather than falsely aborted. | CLOSED |

## Changed-range analysis

The historical source bytes are not retained, so no Git diff was invented. Changed-range analysis used the initial manifest/report, the accepted `W1-RemPlan.md` at SHA-256 `13d77cf3820c3a61dc9905467cb332329ed374917e57a1db4bc64371092a2bbb`, and the current 26-file bytes.

The correction expanded the package from 22 to 26 owned files by splitting contract responsibilities into `authority.py`, `semantic.py`, `operations.py`, `values.py`, `protocols.py` and `state.py`, with corresponding ADR and test changes. Those changes directly address all thirteen accepted Code/State findings. No file under `docs/adr`, `src/garns/backends/contracts`, or `tests/contracts` was present outside the revised manifest.

The original seven State counterexamples are closed. The fresh attack found four defects in changed contract/state surfaces:

- P2-1 is a **NEW ARCHITECTURAL** authority root introduced by exposing runtime freshness and invalidation state as operation arguments.
- P2-2 is a **NEW ARCHITECTURAL** migration-accounting root: the new typed migration outcome is not coupled to the accounting assertion it is supposed to prove.
- P2-3 is a bounded correctness defect in the new phase/evidence grammar.
- P2-4 is a bounded concurrency/ownership defect in the new transaction-use guard.

No other changed-range root was found.

---

## 0. Evidence base

I read the workspace and product instructions, `dev-docs/CurrentProgramCheckpoint.md`, the complete review-loop skill and canonical prompt template, all listed controlling plan/amendment/decision/acceptance documents, `W0-ACCEPTANCE.md`, `docs/PRODUCT_LAYOUT.md`, both prior W1 reviews, `W1-RemPlan.md`, `W1-DRAFT-2.md`, and all 26 manifested files.

Start and end integrity checks included:

```text
shasum -a 256 -c dev-docs/W1-MANIFEST-2.sha256
```

Both checks reported all 26 files `OK`.

```text
shasum -a 256 dev-docs/W1-MANIFEST-2.sha256 dev-docs/W1-DRAFT-2.md \
  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md \
  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md \
  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md \
  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md \
  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md \
  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md \
  dev-docs/GarnsV9-6-W1-ExecutionBrief.md dev-docs/W1-RemPlan.md
```

The results matched every supplied digest, including manifest `3dd854…`, draft `d78c83…`, plan `11268a…`, seam `b99c43…`, D6a/D7/D8 `079517…`, D4/D6b `94b9e5…`, scope amendment `d68cb0…`, its acceptance `dac75f…`, execution brief `1d13f7…`, and remediation plan `13d77c…`.

Manifest coverage comparison:

```text
comm -3 \
  <(rg --files docs/adr src/garns/backends/contracts tests/contracts | sort) \
  <(awk '{print $2}' dev-docs/W1-MANIFEST-2.sha256 | sort)
```

produced no differences.

The prescribed suite passed:

```text
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:src \
/opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .
```

Result: 26 tests, all passing.

Pure in-memory counterexamples reproduced the four findings:

```text
authority stale inputs: TrustedClaims(... valid_until=5.0, invalidation_epoch=7)
commit-phase+rollback-confirmed: CommitOutcome(KNOWN_ABORTED, ...)
equal counterfeit owner entered: TransactionPhase.ACTIVE
MigrationOutcome(..., publication=None)
```

A direct `FrozenMap` duplicate-key probe also showed that its public constructor accepts duplicate keys, but all governed constructors currently reached in the reviewed contract either begin from a Python mapping or require typed values. I did not elevate that bounded representational weakness without a demonstrated durable path.

---

## 1. Findings

### [P2-1] Caller-supplied time and epoch can keep an expired or invalidated context authoritative

**Classification:** **NEW ARCHITECTURAL root cause.**

**Location:** `src/garns/backends/contracts/protocols.py:25-31,39-58,65-69,78-79,87-93`; `src/garns/backends/contracts/authority.py:93-108`; contradicted by `docs/adr/A11-trusted-context.md:18-23` and `docs/adr/A9-configuration.md:4-6`.

**Violated invariant:** validity and invalidation are runtime-owned authority barriers. Request data must not choose the clock or host invalidation epoch used to authorize effects or protected delivery.

**Reproduction:** issue a context with `valid_until=5.0` and `invalidation_epoch=7`. At any later real time, call:

```python
issuer.validate(
    context,
    owner_id="owner",
    now=-1_000_000_000.0,
    current_epoch=7,
    scope=scope,
    capability=Capability.QUERY,
)
```

Validation succeeds. Every ordinary protocol exposes the same `now` and `epoch` values as call arguments. A caller that preserves the issuance epoch can therefore keep presenting a stale clock indefinitely; if the host advances its invalidation epoch, the caller can continue presenting the old epoch.

**Impact:** expired or administratively invalidated authority can remain usable for queries, governed mutations, commit requests, migrations, ledger reads and subscription deliveries. The contract has added authority parameters but has not made their freshness authoritative.

**Required correction:** bind each `ContextIssuer` to a runtime-owned monotonic clock and invalidation-epoch source, or pass an opaque runtime-owned validation environment that ordinary callers cannot construct or override. Remove raw `now` and `epoch` from ordinary operation surfaces. Tests may inject a clock/epoch provider when constructing the runtime or issuer, not per protected call.

**Regression test:** issue a short-lived context using a controllable runtime clock, advance that clock past expiry, and verify every protected operation refuses regardless of caller arguments. Advance the runtime epoch and verify the old context refuses. Confirm that no ordinary operation accepts caller-selected freshness or invalidation inputs and that refusal occurs before adapter invocation.

### [P2-2] Data-changing migration outcomes can omit the ledger publication that supposedly accounts for their effects

**Classification:** **NEW ARCHITECTURAL root cause.**

**Location:** `src/garns/backends/contracts/operations.py:83-110,119-122`; `src/garns/backends/contracts/protocols.py:53-55`; `tests/contracts/test_contracts.py:391-396`; contradicted by `docs/adr/A12-migrations.md:11-16`.

**Violated invariant:** every backfill or DDL-induced data change must be atomically represented in the governed ledger/revision transaction, or refuse before effect. A boolean assertion is not effect accounting.

**Reproduction:** construct a valid data-changing request and then a successful outcome with no publication:

```python
request = MigrationRequest(
    before,
    after,
    MigrationDecision(MigrationEffect.BACKFILL, True, True),
    "migration-digest",
)
outcome = MigrationOutcome(after, None)
```

Both objects are accepted. `AsyncConnection.apply_migration()` may return that outcome while conforming to the protocol. The test suite checks only the input boolean and never requires an atomic `LedgerPublication`.

**Impact:** a backend can apply a backfill or DDL-induced row changes, advance the generation, and return a structurally valid result containing no durable revision/effect accounting. Subscribers and replay consumers can then miss committed state changes while the migration is reported successful.

**Required correction:** make migration results exhaustive by effect class. Metadata-only outcomes may carry a generation transition without data publication only after their proof succeeds. Backfill and DDL-data-change outcomes must carry a nonempty, same-scope, new-generation-compatible `LedgerPublication` tied to the request/migration digest, or a typed refusal/indeterminate outcome. Remove or subordinate the freely asserted `atomically_accounted` boolean to the actual typed publication evidence.

**Regression test:** for every migration class, enumerate all outcome constructors. Backfill and DDL-data-change plus `publication=None`, empty effects, wrong scope, wrong generation, wrong transaction identity or wrong payload digest must refuse. A conforming fake must be unable to report successful data-changing migration after effects unless generation advancement and ledger publication are one typed atomic result.

### [P2-3] The cancellation grammar accepts rollback confirmation after commit request and invents a known abort

**Classification:** bounded state-grammar correction.

**Location:** `src/garns/backends/contracts/state.py:104-112`; `tests/contracts/test_contracts.py:300-315`; contradicted by `docs/adr/A7-isolation-retry.md:11-19`.

**Violated invariant:** after a commit request, only durable reconciliation may establish the terminal outcome. Evidence valid for a rollback-requested phase cannot be attached to an incompatible phase to manufacture `KNOWN_ABORTED`.

**Reproduction:**

```python
cancellation_outcome(
    transaction,
    OperationPhase.COMMIT_REQUESTED,
    AbortEvidence.ROLLBACK_CONFIRMED,
)
```

returns `KNOWN_ABORTED`. The implementation validates only the `NOT_STARTED`/`QUEUED` pairing; it treats all other “authoritative” evidence as valid in every phase. The suite covers rollback confirmation only with `ROLLBACK_REQUESTED`.

**Impact:** an implementation or error path can label a transaction aborted after the commit request crossed its decisive boundary. Reuse/retry of its durable identity can then conflict with a commit that actually became durable.

**Required correction:** define the allowed phase/evidence relation exhaustively. `NOT_STARTED` is valid only for `QUEUED`; `ROLLBACK_CONFIRMED` only for a rollback-requested path that has not crossed commit request; durable abort records must be explicitly tied to reconciliation identity. Any incompatible pair must refuse as an invalid state, never infer an outcome.

**Regression test:** take the Cartesian product of `OperationPhase × AbortEvidence` and assert the exact accepted combinations and results. In particular, every `COMMIT_REQUESTED` cancellation remains `INDETERMINATE` absent committed/aborted durable reconciliation, and `ROLLBACK_CONFIRMED` paired with it raises an invalid-state error.

### [P2-4] Transaction ownership uses caller equality rather than genuine owner identity

**Classification:** bounded concurrency/ownership correction.

**Location:** `src/garns/backends/contracts/state.py:135-149`; contradicted by `docs/adr/A3-async-lifecycle.md:4-7`.

**Violated invariant:** one task owns a transaction handle; a different task or caller object cannot become the owner merely by comparing equal.

**Reproduction:**

```python
class Equal:
    def __eq__(self, other):
        return True

guard = TransactionUseGuard(Equal())
guard.enter(Equal())
```

The distinct second object is accepted and the guard enters `ACTIVE`, because line 142 uses `caller != self.owner`. Equivalent failures occur with non-unique value tokens such as equal strings.

**Impact:** two tasks with equal-valued owner tokens can use the same transaction serially without refusal. The `_in_call` flag catches overlapping calls only; child-task retention and handoff after `leave()` remain possible, violating the single-task ownership contract and permitting writes or commit from the wrong task.

**Required correction:** capture an unforgeable owner identity, preferably the actual runtime task identity or a runtime-issued opaque owner token, and compare by genuine identity/provenance rather than equality. Bind the guard at transaction creation and prohibit owner replacement.

**Regression test:** create two distinct tasks and two distinct objects with equality collisions. Only the task/token captured at transaction creation may enter, both during and after the original owner’s call. Equal strings and hostile `__eq__` implementations must not confer ownership; nested and concurrent use must continue refusing.

---

## 2. Invariant analysis

The following attacks did not produce additional findings:

- The original cancellation defect is corrected for rollback acknowledgement loss, connection loss and cleanup timeout: all remain `INDETERMINATE`.
- Durable publication is idempotent by qualified transaction identity and payload digest. Duplicate same-payload publication does not advance the revision; conflicting payload refuses; reconciliation identity survives generation changes and compaction.
- Revision allocation remains scoped by world/deployment and occurs in the publication model rather than request order. Cross-scope committed reconciliation refuses.
- A4 still rejects ordinary sequence allocation as commit order and specifies a per-scope durable publication lock, same-transaction ledger/effects/revision, and wakeups as hints only.
- Snapshot/open/reconnect grammar still closes the registration race: read high-water and rows in one snapshot, register before release, then scan durable revisions after the cursor.
- Delivery cursor construction enforces common scope/generation and `previous < triggered_by <= observed_through`; neutral refreshes advance the internal cursor without inventing a batch.
- Snapshot, delivery, parameter, mutation and ledger values recursively detach nested supported structures. Original mutation of caller-owned lists/dicts/sets no longer changes retained values.
- Context capability instances resist copy, deepcopy, field replacement, direct mutation, deletion, pickle and counterfeit reconstruction. Registry validation checks exact live object identity.
- Claims normalize capability sets and scalar subclasses without retaining caller-owned mutable containers.
- SQLite shutdown no longer claims it can kill a Python thread. The fence rejects late commit authorization and nonquiescent close reports named unresolved transactions rather than terminal closure.
- Pool return remains fail-closed unless protocol, transaction and sanitation states are all clean.
- Retention advances the durable floor before bounded deletion, deletes strictly below the floor, and leaves transaction-identity reconciliation records outside ledger compaction.
- Generation mismatch and below-floor cursors produce typed refetch rather than silent translation.
- Qualified plan origin includes world, IR digest, authored-storage digest and generation; wrong storage or generation refuses before fake adapter invocation.
- External capture remains explicitly deferred and refuses before effect; it was not treated as a failed v9-6 outcome.
- No driver/compiler dependency reversal, SQL/schema-case dispatch, expected-answer dispatch, guessed physical name, or change to the preserved `query`/`question`/`unenforced` semantics was found in the reviewed tuple.
- Real PostgreSQL, SQLite worker, migration-atomicity and fault-cut evidence remain correctly deferred to their later work packages and were not counted as W1 proof.

## 3. Risks and next action

The 26 green tests do not exercise authoritative clock ownership, the complete phase/evidence cross-product, genuine task identity, or the required coupling between a data-changing migration and its ledger publication. The tests therefore cannot support acceptance while P2-1 through P2-4 remain.

The single next action is one consolidated correction for these four findings, followed by fresh exact-tuple review. Because P2-1 and P2-2 are **NEW ARCHITECTURAL** roots discovered after remediation round 1, they consume the remaining architectural-remediation allowance. Any further new architectural root on this object must trigger the review-loop redesign-or-accept stop rather than another silent architecture patch.
