# Garns v9-6 W1 — Code-axis review

**Review object:** all 22 files in `dev-docs/W1-MANIFEST.sha256`, manifest SHA-256 `5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`; controlling draft `dev-docs/W1-DRAFT.md`, SHA-256 `4680ff38273b1958a06b59cfa75b347ff209f88256c7aeefde436f902006d6f5`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, pre-initial-commit SHA-pinned review mode; controlling execution brief SHA-256 `1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`  
**Date:** 2026-10-03  
**Axis:** architecture, interfaces, call graphs and compatibility reality. Independent, adversarial, read-only. The State axis ran in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — six P2 findings block acceptance. I pre-commit to GO on a revision that resolves P2-1 through P2-6 as specified and introduces no new blocking defect.

## 0. Evidence base

I read and checked:

- workspace `AGENTS.md`, `AGENTS_GWZ.md`, the review-loop skill and canonical reviewer template;
- `dev-docs/CurrentProgramCheckpoint.md`;
- the complete W1 execution brief and draft;
- the historical implementation plan, provider-neutral amendment and acceptance, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance, W0 acceptance, and `docs/PRODUCT_LAYOUT.md`;
- all 16 ADR documents (`README.md` plus A1–A15);
- all contract source in `src/garns/backends/contracts/**`;
- all contract tests in `tests/contracts/**`;
- inherited `TypeRef`, `Read`, `WorldIR`, storage-binding and lowering definitions needed to compare the proposed boundary with the retained IR.

Digest checks established:

- all five controlling historical/amendment decision documents matched their stated digests;
- the manifest itself matched `5e04e8e…`;
- all 22 manifest entries passed `shasum -a 256 -c`;
- the complete on-disk inventory under `docs/adr/**`, `src/garns/backends/contracts/**`, and `tests/contracts/**` contained exactly the 22 listed paths, with no unlisted source;
- the controlling draft matched `4680ff38…`;
- start and end manifest/draft checks matched exactly.

The permitted focused suite passed:

```text
Ran 25 tests in 0.001s
OK
```

Passing these tests did not close the findings below: direct counterexamples exercised accepted constructions that the suite does not reject.

## 1. Findings

### [P2-1] The frozen backend protocol has no governed-write, schema, migration, or ledger operation

**Location:** `src/garns/backends/contracts/protocols.py:24-71`; `docs/adr/A2-backend-contract.md:8-14`; execution brief lines 67–70 and 83–86.

**Violated invariant:** W1 must freeze implementable, required, capability-checked contracts for governed mutations, schema inspection, migration, and ledger publication. A2 explicitly says these are required operations, never optional methods that silently disappear.

**Reproduction:** Protocol introspection yields only:

```text
AsyncBackend: open, subscribe
AsyncPool: acquire, release, close
AsyncConnection: execute, begin, consistent_snapshot, sanitize, close
AsyncTransaction: execute, commit, rollback, reconcile
AsyncSubscription: aclose
```

`Plan.noun` accepts only `query` or `question`, so `execute(Plan, ...)` cannot plausibly encode a governed mutation without violating the plan’s own discriminator. `Capability.GOVERNED_WRITE`, `MIGRATE_METADATA`, and `MIGRATE_DATA` are therefore flags with no corresponding callable contract. `MigrationDecision` is only a local classifier; it cannot inspect, lock, execute, publish a generation, or atomically account effects.

**Impact:** W2–W4 cannot implement “the same async protocols” for the central release feature. Each backend must invent additional private interfaces, so parity, authority barriers, atomic ledger/revision coupling, and non-optional capability behavior are not frozen by W1.

**Required correction:** Add explicit lightweight protocols and typed values for governed mutation execution, schema inspection, migration locking/application, generation publication, and ledger/revision outcome. Every supported operation must have an explicit capability/refusal boundary; unsupported operations must remain callable and refuse before effect rather than vanish.

**Closure test:** Protocol-shape tests must enumerate every required operation, prove each I/O member is async, instantiate both SQLite and PostgreSQL capability descriptions against the same required surface, and demonstrate that an unsupported operation returns its typed pre-effect refusal.

### [P2-2] Parameter and result contracts erase retained nominal, list, identity, closed-set, and nested-field semantics

**Location:** `src/garns/backends/contracts/model.py:131-149`; inherited `src/garns/types.py:33-80`; inherited `src/garns/ir.py:190-306,436-445`.

**Violated invariant:** The backend-neutral boundary must be derived faithfully from the qualified IR and preserve semantic types and result structure; it cannot replace them with generic strings or ambiguous positional nesting.

**Reproduction:** `Parameter` and `ResultField` expose only a free-form `type_id: str`, plus a separate nullable bit. The inherited `TypeRef` distinguishes base and storage class, optionality, list cardinality, qualified nominal identity, closed constructors, and referenced carrier. No encoding or validation maps those fields into `type_id`. Thus all of these materially distinct types can be represented by arbitrary strings with no exhaustiveness or compatibility check. Likewise, `ResultShape.nested` is an unlabeled tuple, while inherited `ShowNested` has a named `column`; the contract does not identify which result field owns each nested shape.

A direct construction accepted both `Parameter("x", "Text")` and `Parameter("x", "m.Nominal")`, with no nominal definition, class, list/cardinality, closed constructors, or carrier identity available to a codec.

**Impact:** Backends can choose incompatible parameter codecs and result decoders while satisfying the protocol. Nominal identities can be confused with plain text, list values with scalar values, and nested results can be attached to the wrong output field. Cross-backend semantic parity becomes unverifiable.

**Required correction:** Define one immutable backend-neutral type descriptor that losslessly carries the relevant `TypeRef` semantics, and use it for parameters and result fields. Nested result nodes must carry stable qualified field identity/ownership rather than positional shapes alone. Add validation from inherited IR into this descriptor.

**Closure test:** Convert representative builtin, optional, list, nominal, closed-set, carrier-identity, and nested-show IR types into contract shapes and assert lossless distinctions and deterministic round trips. Mutants that erase each semantic dimension must fail.

### [P2-3] `Plan` is neither immutable nor bound to its originating world/storage contract

**Location:** `src/garns/backends/contracts/model.py:152-173`; ADR A2 lines 3–6; implementation plan lines 66–75 and 194–224.

**Violated invariant:** W1 promises one immutable plan derived from qualified IR and explicit `WorldIR` storage binding, with no inferred physical/default binding and no accidental cross-deployment execution.

**Reproduction:** `Plan.root` is typed as unrestricted `object`, and the frozen dataclass performs no defensive copy or validation:

```text
root = []
plan = Plan("m.q", "query", (), ResultShape(()), root)
root.append("mutated")
plan.root == ["mutated"]
```

The same plan has no world, deployment-independent binding identity, IR digest, storage-binding digest, schema generation, or equivalent provenance. It can therefore be passed unchanged to a connection opened for another `QualifiedDeployment`, even where authored physical bindings differ.

**Impact:** A caller can mutate a supposedly frozen plan after validation, or execute a plan against the wrong bound storage. Dialect packages cannot reliably prove that physical names came from the selected `WorldIR`, and prepared/cache keys cannot safely distinguish binding or generation changes.

**Required correction:** Replace unrestricted `object` with a closed immutable W2-owned node protocol/union placeholder that cannot contain mutable unchecked payloads. Add an immutable plan-origin descriptor sufficient to bind or validate the qualified world/storage/generation contract without embedding SQL or inventing the W2 node algebra.

**Closure test:** Attempts to mutate any reachable plan component must fail or leave the plan unchanged. Executing a plan against a mismatched world/storage digest or generation must produce a typed pre-effect refusal. Equivalent plans from different authored bindings must not compare or cache as interchangeable.

### [P2-4] Ordinary query and snapshot calls cannot enforce the required trusted-context boundary

**Location:** `src/garns/backends/contracts/protocols.py:34-42,60-71`; ADR A11 lines 3–15; D6a/D7/D8 decision lines 61–77; execution brief lines 87–89.

**Violated invariant:** Execute, transaction and subscription entry points derive scope, capability and writer authority from a genuine request-owned context, with validation at entry and relevant delivery/effect barriers.

**Reproduction:** `AsyncConnection.execute(plan, parameters)` and `consistent_snapshot(plan, parameters)` accept no `TrustedContext`. The connection cannot inherit one during opening: `AsyncBackend.open(scope, deadlines)` accepts a raw `QualifiedDeployment`, not a context or context-bound runtime handle. Only `begin` and `subscribe` receive context.

Consequently, an acquired connection exposes reads and snapshots with neither request ownership nor query capability input. The protocol provides no means to validate context expiry/invalidation at those calls.

**Impact:** Implementations must either leave query disclosure unauthorised or introduce an undocumented side channel/private wrapper outside the frozen contract. Caller-supplied scope enters `open` directly, contrary to the rule that ordinary caller data cannot supply or widen scope.

**Required correction:** Make authority flow explicit through open/acquire/execute/snapshot, either by binding a validated context to a request-scoped runtime/connection handle or by passing it to every authority-bearing operation. The contract must make raw scope opening privileged/internal and distinguish it from ordinary execution.

**Closure test:** Protocol-level hostile tests must show that missing, counterfeit, cross-owner, expired, invalidated, scope-conflicting, and capability-deficient contexts refuse before execute and snapshot work. A connection obtained under one owner must not be usable by another request.

### [P2-5] `TrustedContext` is serializable and serialization discloses its supposedly redacted claims

**Location:** `src/garns/backends/contracts/model.py:253-281`; ADR A11 lines 3–8; provider-neutral acceptance lines 57–64.

**Violated invariant:** The provider-neutral capability must be non-serializable and minimally disclosing; raw normalized identity, writer and scope must not escape through Garns-owned serialization.

**Reproduction:** Standard-library pickle accepts the object:

```text
pickle_len 282
[b'SECRET_PRINCIPAL', b'SECRET_WRITER', b'SECRET_WORLD']
```

`__repr__` redaction does not affect dataclass serialization. Although the unpickled issuer token will not validate against the original runtime token, the sensitive claims have already been disclosed.

**Impact:** Logging, caching, IPC, evidence collection, or generic framework serialization can export principal, writer, scope and capability data despite the documented non-serialization guarantee. The current test checks only `repr`.

**Required correction:** Explicitly reject serialization/copy protocols on `TrustedContext` and ensure any supported diagnostic form is redacted. Keep issuer state and claims inaccessible to generic serializers to the extent promised by the in-process contract.

**Closure test:** Hostile tests using pickle, copy/deepcopy, dataclass conversion and the project’s output/evidence serializers must either refuse or yield a documented redacted form containing none of the seeded canary fields.

### [P2-6] Cancellation is classified as known-aborted from request timing alone

**Location:** `src/garns/backends/contracts/state.py:37-40`; `tests/contracts/test_contracts.py:74-78`; ADR A3 lines 9–13; ADR A7 lines 11–17.

**Violated invariant:** Task cancellation is not a database outcome. `KNOWN_ABORTED` requires authoritative database knowledge; cancellation before commit request must first complete or establish rollback.

**Reproduction:** `cancellation_outcome(transaction, commit_requested=False)` always returns `KNOWN_ABORTED`. The function accepts no rollback result, transaction status, connection disposition, or authoritative abort evidence. A concrete sequence is:

1. a statement has begun;
2. the task is cancelled before commit request;
3. interrupt/quiescence or rollback is attempted;
4. the connection is lost or cleanup deadline expires before rollback is confirmed;
5. the helper is called with `False` and reports `KNOWN_ABORTED`.

**Impact:** Callers may suppress reconciliation or safely-retry checks for work whose database outcome was never established. This contradicts the three-way terminal grammar and can lead to duplicate effects once mutation execution exists.

**Required correction:** Model cancellation phase separately from terminal database knowledge. Return `KNOWN_ABORTED` only after authoritative rollback/abort completion; otherwise retain an unresolved/indeterminate outcome and discard the connection as appropriate.

**Closure test:** Add state-table tests for cancellation while queued, during statement, after writes, during rollback, rollback timeout/connection loss, before commit request, and after commit request. Only traces with confirmed rollback may end `KNOWN_ABORTED`.

## 2. Invariant analysis including failed attacks

- **Tuple integrity held.** The exact 22-file inventory and every listed digest matched at both review boundaries.
- **Driver isolation held.** Contract source imports no Psycopg, SQLite, SQL text, parser nodes, or driver cursors.
- **Async declaration shape held for existing I/O methods.** Every declared I/O-bearing protocol member is async except the intentionally synchronous `__aiter__`. This does not cure the missing operations in P2-1.
- **Publication ordering model resisted the request-order attack.** Its reference model assigns revisions only at `publish_committed`, so reverse request/commit order and rollback gaps behave as documented.
- **Delivery watermark validation held.** `Delivery` rejects cross-scope, cross-generation and reversed `triggered_by`/`observed_through` cursors, preventing later state from being labeled as an earlier revision.
- **Connection sanitation direction held.** Any non-idle or unsanitized predicate produces `DISCARD`.
- **Capability refusal exists but is disconnected from operations.** `BackendCapabilities.require()` correctly yields a typed refusal, but no protocol requires it at the governed operations absent under P2-1.
- **Context issuer identity, owner, expiry and epoch checks held when explicitly invoked.** A structural copy with a different issuer token cannot validate. The attack instead succeeded at serialization and at protocol call paths where context is unavailable.
- **Migration classification partially held.** The pure classifier refuses observable metadata-only changes and unaccounted data-changing classes. It does not supply the required migration execution/publication interface.
- **No forbidden external-capture implementation appeared.** A5 records deferral and the capability/refusal vocabulary does not introduce a speculative capture adapter.
- **SQLite/PostgreSQL support declarations were scoped honestly.** The ADRs distinguish target matrices from later real-server evidence and retain the selected SQLite and PostgreSQL version obligations.
- **The test suite is pure and fast but insufficiently falsifying.** It proves selected constructor branches and helper outputs; it does not attack absent protocol operations, lossy types, mutable/cross-binding plans, missing execute authority, serialization, or rollback-failure cancellation traces.

## 3. Risks and next action

Residual implementation evidence—event-loop responsiveness, real PostgreSQL 15–18 execution, SQLite version coverage, fault cuts, migration atomicity and compaction races—properly remains deferred to W3–W7 and is not a defect in this W1 review.

The blocking problems are W1 interface defects, not demands for W2 algebra or W4 implementation. The next action is one consolidated W1 remediation that:

1. completes the required governed/schema/migration/ledger protocol;
2. replaces lossy type/result descriptors;
3. makes plans immutable and binding-aware;
4. carries trusted authority through all relevant calls;
5. prevents context serialization/disclosure; and
6. corrects cancellation knowledge semantics.

The revised tuple then needs focused Code re-verdict against the original counterexamples and corresponding State review under the normal review loop.
