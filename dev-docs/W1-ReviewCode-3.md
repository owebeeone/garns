# Garns v9-6 W1 corrected architecture package — CODE-AXIS REVIEW, ROUND 3

**Review object:** all 26 files in `dev-docs/W1-MANIFEST-3.sha256`, manifest SHA-256 `3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`; corrected W1 architecture package, remediation 2; controlling draft `dev-docs/W1-DRAFT-3.md`, SHA-256 `6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; controlling implementation plan SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; execution brief SHA-256 `1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`  
**Date:** 2026-10-03  
**Axis:** architecture, interfaces, call graphs and compatibility reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks acceptance. The final remediation closes the round-2 delivery-interface counterexample, but the original Code P2-5 nondisclosure counterexample is not closed: the opaque context directly exposes and permits serialization of its complete claims. This is an **UNCLOSED ORIGINAL ARCHITECTURAL root**, not a new round-3 root. Two architectural remediation rounds have been used, so the lane must stop for operator redesign-or-accept rather than begin another architecture patch.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Initial Code P2-1 | Complete governed mutation, schema inspection, migration and ledger/publication operations | Re-enumerated the five protocols. Query/snapshot, governed mutation and commit, schema inspection, migration lock/application, ledger replay, subscription binding and lifecycle operations remain present. Required I/O members are async except the intentionally synchronous iterator-binding factory. Both backend descriptions retain the common capability surface and typed pre-effect refusal. | CLOSED |
| Initial Code P2-2 | Preserve every inherited `TypeRef` dimension and named nested-result ownership | Re-traced inherited `TypeRef.base`, `cls`, optionality, list cardinality, nominal identity, closed constructors and carrier identity through `SemanticType.from_type_ref()`. `ResultShape` requires unique field identities and each `NestedResult` names a field owner. | CLOSED |
| Initial Code P2-3 | Immutable opaque plan root plus authored binding and generation provenance | `FrozenPlanRoot` requires exact owned `bytes`; `PlanOrigin` records world, IR digest, authored-storage digest and generation; `BindingIdentity.validate_plan()` distinguishes binding from generation mismatch before execution. Mutable-root and wrong-binding constructions no longer satisfy the contract. | CLOSED |
| Initial Code P2-4 | Carry genuine trusted authority through ordinary protected operations | Ordinary open, acquire/release, execute, snapshot, transaction, mutation, migration, ledger replay and subscription entry carry only `TrustedContext`. Runtime-owned time, epoch and task providers replaced caller-selected freshness and ownership parameters. | CLOSED |
| Initial Code P2-5 | Make contexts opaque, non-copyable, non-reconstructable, non-serializable and nondisclosing | Copy, deepcopy, replacement, direct field mutation, whole-context pickle and counterfeit-instance validation refuse. However, the exact issued context exposes its complete `TrustedClaims` as `context._claims`; those claims have a revealing dataclass representation and are directly pickleable. The original seeded-canary disclosure attack succeeds. | **OPEN — P2-1 below** |
| Initial Code P2-6 | Separate cancellation phase from authoritative database knowledge | Re-ran the complete phase/evidence relation. Only queued/not-started and rollback-requested/rollback-confirmed yield known abort. Commit-requested plus rollback-confirmed and all other incompatible pairs refuse; unresolved commit evidence remains indeterminate. | CLOSED |
| Round-2 Code P2-1 | Remove direct subscription iteration and expose one authority-bound iterator graph | `AsyncSubscription` has only `bind_delivery(context)` and `aclose`; it has no `__aiter__`, `__anext__`, or parallel delivery method. The concrete `AuthorityBoundIterator.__anext__` validates before read and after the awaited read. Close and renewal prevent an in-flight old iterator from delivering. Actual `async for` over the bound iterator refuses after expiry, epoch change, exact-context invalidation or task-owner change. | CLOSED |

## Changed-range analysis

Historical source bytes are not retained, so no Git diff was invented. Analysis used both prior-round reports, `W1-RemPlan.md` SHA-256 `13d77cf3820c3a61dc9905467cb332329ed374917e57a1db4bc64371092a2bbb`, `W1-RemPlan-2.md` SHA-256 `ecd13b9b63981e9ad66bdaa83a141760c63544be1639380dc8a823fd09dafa83`, the historical manifests and reports, and the current 26-file bytes.

The round-3 tuple changes the shared authority, subscription, migration, cancellation and transaction-owner boundaries exactly where `W1-RemPlan-2.md` required:

- runtime-owned clock, epoch and current-task providers replace caller freshness/owner inputs;
- a subscription is no longer directly iterable and binds one concrete authority-aware iterator;
- iterator validation occurs before and after an awaited read, while close/renewal suppress old in-flight delivery;
- migration success is coupled to its exact request and typed publication evidence;
- cancellation accepts an explicit closed phase/evidence relation;
- transaction ownership is captured and checked by genuine object identity.

Those corrections close all five round-2 findings and preserve the other initial counterexample fixes.

The remaining finding is not caused by the round-3 changed range. It is an **UNCLOSED ORIGINAL ARCHITECTURAL root** from initial Code P2-5: `TrustedContext` still stores all normalized claims in a caller-readable instance slot. Earlier closure checks established that the context object itself could not be copied or serialized, but did not independently attack serialization and diagnostic disclosure through its reachable `_claims` object. The final tuple still violates the original nondisclosure disposition.

No unlisted file was found under `docs/adr`, `src/garns/backends/contracts`, or `tests/contracts`.

---

## 0. Evidence base

I read:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- the controlling implementation plan, provider-neutral seam amendment and acceptance, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance, W1 execution brief, W0 acceptance, and `docs/PRODUCT_LAYOUT.md`;
- both initial W1 reports, `W1-RemPlan.md`, both round-2 W1 reports, and `W1-RemPlan-2.md`;
- `W1-DRAFT-3.md`;
- all 26 manifested files: A1–A15 plus the ADR index, all eight contract modules, and both contract-test files;
- retained `src/garns/types.py` definitions and relevant retained IR/storage semantics used to check the semantic boundary.

Start and end checks produced the required tuple:

```text
3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13  dev-docs/W1-MANIFEST-3.sha256
6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566  dev-docs/W1-DRAFT-3.md
ecd13b9b63981e9ad66bdaa83a141760c63544be1639380dc8a823fd09dafa83  dev-docs/W1-RemPlan-2.md
```

The controlling document digests matched the prompt, including implementation plan `11268a…`, provider-neutral seam `b99c43…`, D6a/D7/D8 `079517…`, D4/D6b `94b9e5…`, governed-write amendment `d68cb0…`, its acceptance `dac75f…`, execution brief `1d13f7…`, and first remediation plan `13d77c…`.

Both executions of:

```text
shasum -a 256 -c dev-docs/W1-MANIFEST-3.sha256
```

reported all 26 paths `OK`.

The inventory comparison:

```sh
comm -3 \
  <(rg --files docs/adr src/garns/backends/contracts tests/contracts | sort) \
  <(awk '{print $2}' dev-docs/W1-MANIFEST-3.sha256 | sort)
```

produced no differences.

The prescribed focused suite passed:

```text
..................................
----------------------------------------------------------------------
Ran 34 tests in 0.009s

OK
```

I independently re-ran the original nondisclosure attack using an issued context seeded with canaries. The exact context’s redacted `repr` did not disclose them, but direct access and serialization of its reachable claims did:

```text
TrustedContext(context_id=<redacted>, scope=<redacted>, claims=<redacted>)
TrustedClaims(principal='principal-CANARY',
              writer='writer-CANARY',
              scope=QualifiedDeployment(world='WORLD-CANARY',
                                        deployment='DEPLOY-CANARY'),
              capabilities=frozenset({GOVERNED_WRITE}),
              context_id='context-CANARY',
              valid_until=10.0,
              invalidation_epoch=7)
claim_pickle_bytes 276
principal-CANARY True
writer-CANARY True
WORLD-CANARY True
DEPLOY-CANARY True
context-CANARY True
```

The pure in-memory probe used the prescribed Python 3.14 `-B`, `PYTHONDONTWRITEBYTECODE=1`, cached dependency path and product `src`. It modified no file and contacted no service.

---

## 1. Findings

### [P2-1] The supposedly opaque context directly exposes serializable trusted claims

**Classification:** **UNCLOSED ORIGINAL ARCHITECTURAL root** from initial Code P2-5. This is not a new round-3 root.

**Location:** `src/garns/backends/contracts/authority.py:25-37,49-64`; specifically storage at line 29 and retrieval at line 60. Contradicted by `docs/adr/A11-trusted-context.md:3-12,27-30`, which requires an opaque, non-serializable, redacted context whose claims do not disclose through serialization. The existing hostile-disclosure tests in `tests/contracts/test_contracts.py` attack the context wrapper but do not traverse and serialize its reachable `_claims`.

**Violated invariant:** An ordinary recipient of `TrustedContext` must receive an opaque authority handle, not a readable claims record. Context copying, reconstruction, dataclass conversion and serialization must neither mint authority nor disclose principal, writer, qualified scope, capability set, context identity, validity deadline or invalidation epoch.

**Reproduction:** Issue a valid context with seeded claim canaries, then execute:

```python
claims = context._claims
print(claims)
blob = pickle.dumps(claims)
```

`TrustedContext.__repr__` is redacted and `pickle.dumps(context)` refuses, but `_claims` is an ordinary caller-readable slot holding a frozen dataclass. Its generated `repr` prints every field, and standard pickle serializes all fields. The executed probe found every seeded principal, writer, world, deployment and context-identity canary in the pickle bytes.

The leading underscore is a naming convention, not an access boundary. No mutation, reflection exploit, counterfeit construction or implementation-private privilege is required; every operation is ordinary Python attribute access on the exact issued object supplied to protected calls.

**Impact:** Any component receiving the opaque execution capability can extract and persist the complete trusted claim set despite the frozen A11 nondisclosure contract. This expands disclosure beyond the deliberately redacted diagnostic surface and permits claims to leak through application logs, exception reporting, telemetry, caches, queues or serialized artifacts. The extracted record does not itself pass exact-instance authority validation, so this is not authority minting, but it is a concrete security and compatibility failure in the frozen trusted-context representation.

**Required correction:** Do not store claim material on the caller-held context object. The runtime authority registry should own claims and task provenance keyed by exact live context identity, while the public context contains no caller-readable claims record. Validation should retrieve claims exclusively from issuer-owned registry state after exact-instance lookup. Diagnostic and serialization attacks must traverse every reachable context attribute, not only invoke protocols on the wrapper. If Python-level inspection remains intentionally permitted, A11 must be redesigned to state that disclosure explicitly; the current “opaque,” “redacted,” and serialization-nondisclosure promises cannot coexist with `_claims`.

**Closure test:** Seed unique canaries in every claim field, issue a context, and recursively inspect all attributes reachable through ordinary access, slots, dataclass helpers, copying, reduction and serialization protocols. Neither textual output nor serialized bytes may contain a canary. The issuer must still validate the exact live object and return issuer-owned claims internally; copy, reconstruction and a distinct lookalike must remain unauthorized. Expiry, invalidation and owner checks must continue using the registry-owned record.

Because this is an unresolved architectural trust-boundary defect after both permitted architectural remediation rounds, closure requires the review-loop lane stop and an operator redesign-or-accept decision. It is not eligible for an unreviewed third architecture patch.

---

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Round-2 delivery counterexample:** `AsyncSubscription` no longer exposes `__aiter__`, `__anext__`, or `next_delivery`. Actual intended syntax is `async for item in subscription.bind_delivery(context)`, and the returned concrete iterator validates authority before and after its awaited reader.
- **Renewal and close during read:** closing or renewing the old iterator while its reader is suspended causes the resumed old `__anext__` to terminate before delivery. Advancing the runtime epoch, expiring or exactly invalidating the context during the read causes post-await validation to refuse before returning rows.
- **Task ownership:** runtime authority records the actual current-task object and compares by identity. Equal-valued tokens, hostile equality implementations and child tasks do not confer ownership.
- **Runtime-owned freshness:** ordinary protected-operation signatures do not accept `now`, epoch or owner overrides. Time, invalidation epoch and task identity come from trusted setup providers.
- **Migration result coupling:** metadata-only success requires a proof digest and no publication. Data-changing success requires nonempty typed effects, exact requested binding, matching scope and generation, `migration:<request-digest>` identity and matching payload digest. Refused and indeterminate results are distinct non-success values.
- **Cancellation:** the complete phase/evidence Cartesian relation rejects incompatible combinations. Commit-requested cancellation cannot infer abort from rollback confirmation; durable terminal findings enter through identity-bound reconciliation.
- **Operation completeness:** both backend protocols retain query, snapshot, mutation, schema, migration, ledger and lifecycle methods. Capability absence remains an explicit pre-effect refusal rather than a missing optional method.
- **Driver/compiler isolation:** contract modules import no database driver, SQLite lowering, parser, resolver, SQL string or schema-case dispatch. The opaque W2 plan root remains canonical bytes rather than a second expression algebra.
- **Semantic type fidelity:** `SemanticType.from_type_ref()` carries every retained `TypeRef` dimension. Nested results have named owners and result fields have unique qualified identities.
- **Immutable plan and values:** plan roots require exact bytes; parameter, result, mutation, snapshot, delivery and ledger structures detach supported nested values. Binding identity validates world, IR digest, authored storage digest and generation.
- **Publication/reconciliation identity:** qualified transaction identity and payload digest preserve idempotence, reject conflicting reuse and survive generation changes and ledger compaction in the reference model.
- **Snapshot/replay shape:** cursor and delivery constructors enforce common qualified scope/generation and strict `previous < triggered_by <= observed_through` ordering. Generation and retained-floor failures remain typed refetch paths.
- **SQLite shutdown fence:** new commit authorization cannot cross shutdown; nonquiescent close names unresolved transactions instead of claiming rollback or thread termination.
- **Language preservation:** no numbered-case execution, expected-answer dispatch, inferred storage name, schema-name dispatch or change to `query`, `question`, `unenforced`, qualification or authored-binding semantics was found.
- **Deferrals:** external capture remains explicitly deferred and refuses before effect. Real PostgreSQL, SQLite worker, migration atomicity, live delivery and fault-cut evidence remain later-package obligations and were not treated as W1 accomplishments.

A bounded validation weakness remains below the blocking threshold: `MigrationDecision` does not normalize its `effect` field to `MigrationEffect`, so an arbitrary string can enter the data-changing branch when accompanied by full publication evidence. This fails closed toward the strongest accounting obligations and does not create an unaccounted-success path in the reviewed reference model; it is not elevated to a separate finding.

---

## 3. Risks and next action

The 34 passing contract tests do not exercise disclosure through attributes reachable from the exact issued context. Their green result therefore cannot establish the original A11 nondisclosure closure.

The single next action is to stop the W1 lane and obtain an operator redesign-or-accept decision for P2-1. The architecture can be redesigned so claim material exists only in issuer-owned registry state, or the operator can explicitly accept a weaker, inspectable-context disclosure contract and amend the controlling documents. Two architectural remediation rounds have already been used; no third architecture correction is authorized under the review-loop cap.
