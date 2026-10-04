# Garns v9-6 W1 corrected architecture package — CODE-AXIS REVIEW, ROUND 2

**Review object:** all 26 files in `dev-docs/W1-MANIFEST-2.sha256`, manifest SHA-256 `3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6`; corrected remediation-round-1 package; controlling draft `dev-docs/W1-DRAFT-2.md`, SHA-256 `d78c83ddcce4e1660bed3ab3e36b3b473b05c5e28d0fc2c638479abc4a9b4569`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; controlling implementation plan SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; execution brief SHA-256 `1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`  
**Date:** 2026-10-03  
**Axis:** architecture, interfaces, call graphs and compatibility reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — the six prior Code findings are closed, but one new P2 architectural finding blocks acceptance. I pre-commit to GO on a revision that resolves P2-1 as specified and introduces no new blocking defect.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Code P2-1 | Complete governed mutation, schema inspection, migration and ledger/publication operations | Re-enumerated `AsyncBackend`, `AsyncPool`, `AsyncConnection`, `AsyncTransaction` and `AsyncSubscription`; all required I/O methods exist and are async. Both-backend capability fakes retain the same required surface and refuse unsupported work before fake adapter invocation. | CLOSED |
| Code P2-2 | Preserve every inherited `TypeRef` dimension and name nested result ownership | Re-traced builtin, optional, list, nominal, closed-constructor, carrier and named nested-result cases through `SemanticType`, `ResultField`, `NestedResult` and `ResultShape`; dimension-erasure mutants compare unequal. | CLOSED |
| Code P2-3 | Immutable opaque root plus world/storage/generation-aware plan origin | Re-ran mutable-root rejection and wrong-storage/wrong-generation traces. `FrozenPlanRoot` accepts owned exact `bytes`; `BindingIdentity.validate_plan()` refuses mismatches before fake invocation. | CLOSED |
| Code P2-4 | Carry genuine trusted authority through ordinary open/acquire/execute/snapshot and protected operations | Re-ran missing/counterfeit, wrong-owner, expired, invalidated, wrong-binding and insufficient-capability traces for open/acquire/execute/snapshot/begin. The original unauthenticated execute/snapshot counterexample no longer conforms to those method signatures. The newly found subscription iterator bypass is a separate delivery-interface root and is reported below. | CLOSED |
| Code P2-5 | Refuse copying, reconstruction, dataclass conversion and serialization; redact diagnostics | Re-ran copy, deepcopy, replace, pickle, `asdict`, direct field replacement/deletion and canary-repr attacks. They refuse or disclose no seeded claims; a reconstructed distinct object does not validate. | CLOSED |
| Code P2-6 | Separate cancellation phase from authoritative database knowledge | Re-ran queued, statement, writes-applied, rollback-requested, rollback-ack-loss, connection-loss, cleanup-timeout and commit-requested traces. Only not-started and authoritative abort/rollback evidence produce `KNOWN_ABORTED`; the original pre-commit cancellation counterexample remains `INDETERMINATE`. | CLOSED |

## Changed-range analysis

Old source bytes are not retained, so I did not invent a textual Git diff. I compared the historical and corrected manifests, prior reports, merged remediation plan, current hashes and current bytes.

The corrected tuple adds cohesive `authority.py`, `operations.py`, `semantic.py` and `values.py` modules and changes the shared contract surface in `__init__.py`, `model.py`, `protocols.py`, `state.py`, `tests/contracts/test_contracts.py`, ADRs A2/A3/A4/A7/A8/A11 and `docs/adr/README.md`. Unrelated ADRs remain hash-identical where the remediation did not require changes. These changes match the accepted dispositions: operation completion, immutable semantic/value boundaries, plan provenance, authority propagation, cancellation knowledge, publication identity and SQLite shutdown fencing.

The new finding lies in the changed authority/subscription interface: remediation added an authority-bearing `next_delivery(...)` method but retained a second, ordinary `async for` delivery path through `__aiter__`/`__anext__` that carries no authority. This is a **NEW ARCHITECTURAL root cause**: the protocol exposes two competing delivery call graphs, only one of which can honor A11’s required per-delivery barrier.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md` and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer prompt;
- the controlling implementation plan, provider-neutral seam and acceptance, D6a/D7/D8 and D4/D6b decisions, governed-write amendment and acceptance, W1 execution brief, W0 acceptance and `docs/PRODUCT_LAYOUT.md`;
- the initial Code and State reports and the merged remediation plan as legitimate round-2 inputs;
- the corrected controlling draft;
- all 26 manifest files: 16 ADR documents, all eight contract modules and both contract-test files;
- retained `TypeRef` definitions used to check the semantic boundary.

Start and end verification both produced:

```text
3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6  dev-docs/W1-MANIFEST-2.sha256
d78c83ddcce4e1660bed3ab3e36b3b473b05c5e28d0fc2c638479abc4a9b4569  dev-docs/W1-DRAFT-2.md
11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512  dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md
b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01  dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md
079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f  dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md
94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce  dev-docs/GarnsV9-6-OperatorDecisions-D4-D6b.md
d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md
dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799  dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md
1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344  dev-docs/GarnsV9-6-W1-ExecutionBrief.md
13d77cf3820c3a61dc9905467cb332329ed374917e57a1db4bc64371092a2bbb  dev-docs/W1-RemPlan.md
```

`shasum -a 256 -c dev-docs/W1-MANIFEST-2.sha256` reported `OK` for every entry at both boundaries. Comparing `rg --files docs/adr src/garns/backends/contracts tests/contracts` with the manifest produced no difference.

The required focused suite passed:

```text
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.007s

OK
```

I also ran a pure in-memory conforming-subscription counterexample. It produced:

```text
runtime_conforms True
delivered_without_context (FrozenMap(items_tuple=(('secret', 'disclosed'),)),)
```

No files, bytecode, repositories, databases or services were modified.

## 1. Findings

### [P2-1] Subscription delivery has an authority-free iterator path

**Classification:** **NEW ARCHITECTURAL root cause.**

**Location:** `src/garns/backends/contracts/protocols.py:73-80`; `docs/adr/A11-trusted-context.md:13-23`; `docs/adr/README.md:84-87`. The tests enumerate both `next_delivery` and `__aiter__` but contain no fake subscription proving that ordinary iteration crosses the authority barrier (`tests/contracts/test_contracts.py:369-382,404-452`).

**Violated invariant:** A11 requires context/owner/time/epoch revalidation before each subscription delivery, with zero staleness at that boundary. The async-facing subscription contract must not expose a second delivery mechanism that cannot carry those inputs.

**Reproduction:** `AsyncSubscription.next_delivery(context, owner_id, now, epoch)` can revalidate authority, but normal Python iteration does not call that method. `async for item in subscription` calls `subscription.__aiter__()` and then iterator `__anext__()` with no arguments. A runtime-checkable fake can therefore:

1. expose the required `cursor`;
2. implement `next_delivery(...)` to reject or assert that authority is required;
3. implement `__aiter__`/`__anext__` to return a `Delivery` directly;
4. satisfy `isinstance(fake, AsyncSubscription)`;
5. disclose rows through `async for` without any context, owner, time, epoch, expiry or invalidation check.

The executed counterexample conformed structurally and delivered `{"secret": "disclosed"}` without invoking `next_delivery`.

**Impact:** An implementation can conform to the frozen protocol while the intended public consumption syntax bypasses expiry, invalidation and ownership checks after subscription creation. A context valid at subscribe time can expire or be invalidated while the iterator continues disclosing later committed state. This contradicts the accepted zero-staleness authority boundary and leaves W3 with mutually inconsistent call graphs.

**Required correction:** Freeze one delivery call graph. Either:

- make the iterator itself a request-bound, runtime-owned object whose `__anext__` performs the required live validation from an unforgeable authority binding, and remove the misleading parallel `next_delivery` path; or
- do not expose the subscription directly as an async iterator, and require an authority-bearing method/resource that returns a short-lived iterator whose every `__anext__` revalidates the bound context.

The protocol and ADR must state how renewal replaces the bound delivery authority without allowing a stale iterator to continue. Merely documenting that implementations should have `__anext__` call `next_delivery` is insufficient because `__anext__` has no fresh `now`/epoch/context inputs and structural conformance cannot enforce that call.

**Closure test:** Build a runtime-checkable conforming fake and exercise the actual intended `async for` syntax. Between two deliveries, expire the context, advance invalidation epoch, invalidate the exact issued object, change owner, and attempt use from a retained child task. Every second delivery must refuse before reading or returning rows, and there must be no alternate protocol-conforming iterator that can emit a `Delivery` without crossing the same barrier.

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Operation completeness:** the common protocol now includes governed mutation, schema inspection, migration locking/application, generation-bearing migration outcomes, ledger replay and commit publication. I found no required W1 operation silently represented only by a capability flag.
- **Driver/compiler isolation:** contract source imports neither Psycopg nor SQLite, SQL text, parser/resolver nodes or driver cursors. `FrozenPlanRoot` remains an opaque W2 product rather than a second expression algebra.
- **Qualified authored plan provenance:** plan origin carries world, IR digest, storage digest and generation. Binding validation distinguishes storage/binding mismatch from generation mismatch before fake invocation.
- **Semantic type fidelity:** the corrected descriptor preserves base, storage class, optionality, list cardinality, nominal identity, closed constructors and carrier identity. Nested results name an owning qualified field.
- **Immutable values:** parameter, mutation, snapshot, delivery and ledger value constructors recursively detach supported structured values and reject arbitrary mutable/custom values.
- **Context genuineness and nondisclosure:** exact live instance identity is registry-backed. Copying, deep copying, replacement, reconstruction, pickle and dataclass conversion cannot mint authority; repr and refused serialization do not disclose canaries.
- **Ordinary protected calls:** open, acquire/release, execute, snapshot, transaction entry/mutation/commit/reconcile, schema inspection, migration and ledger replay carry authority inputs. Host-only raw binding open is separately named.
- **Cancellation knowledge:** phase and evidence are independent; cancellation timing alone no longer establishes abort. Missing final evidence remains indeterminate.
- **Publication identity:** qualified transaction identity plus payload digest makes same-payload repetition idempotent and conflicting reuse a typed refusal; identity results intentionally survive generation/retention transitions.
- **Shutdown fencing:** the reference fence rejects a commit newly requested after shutdown and reports begun unresolved work rather than falsely claiming terminal close.
- **Language preservation:** the package introduces no schema-name dispatch, numbered-case execution, guessed physical names or query/question reinterpretation. `Plan.noun` preserves query/question distinction and only questions admit a live bound.
- **External capture:** A5 consistently refuses the deferred feature before effect and does not introduce a speculative source adapter.
- **Evidence honesty:** the ADRs and draft consistently label PostgreSQL, SQLite responsiveness, migration atomicity and live backend behavior as later evidence, not accomplishments of these reference contracts and fakes.

## 3. Risks and next action

The package remains correctly limited to contracts, reference models and conforming fakes; it does not prove real PostgreSQL, SQLite worker, migration, fault-cut or live-delivery behavior. Those are legitimate later gates.

The blocking issue is not deferred implementation evidence: it is an internally contradictory frozen delivery interface. The single next action is the remaining bounded architectural remediation round for P2-1, aligning the async-iterator call graph with A11’s genuine per-delivery authority barrier and adding the stated `async for` regression attacks. Because this is a new architectural root after remediation round 1, it consumes the remaining architectural remediation allowance; another new architectural root on the resulting object must stop the lane for operator redesign-or-accept rather than begin a third architectural patch.
