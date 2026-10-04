# W2 shared query-planning design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`; design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6` design-review manifest SHA-256 `4014506528289e2d7d31c45ca433960271c8e5c3dd0e8486a7f53a183a425881`. Sources were read directly from the SHA-pinned filesystem tuple under the accepted no-Git exception; no Git-derived cleanliness or revision was assumed.  
**Date:** 2026-10-03  
**Axis:** Internal coherence and agreement with the controlling contract, accepted W1 tuple, inherited IR, lowering, result, footprint and ownership behavior. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three bounded P2 findings block. I pre-commit to GO on a revision that resolves P2-1, P2-2 and P2-3 as specified.

---

## 0. Evidence base

The exact tuple was verified at both review boundaries:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST.sha256` returned `4014506528289e2d7d31c45ca433960271c8e5c3dd0e8486a7f53a183a425881`.
- The object, brief and testimony hashes were respectively `a7d6b1dc…`, `5320926a…` and `54659f6f…`.
- `shasum -a 256 -c` passed for:
  - `W2-Design-MANIFEST.sha256`;
  - all 48 entries in `W2-DesignSourceInputs.sha256`;
  - all 13 entries in `W2-DesignControlInputs.sha256`;
  - all 26 entries in `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`.
- Inventory counts remained exactly 48, 13 and 26 at start and end. No tuple movement occurred.

I read the complete workspace and product instructions, current checkpoint, review-loop skill and canonical reviewer template; the full W2 execution brief, design and builder testimony; the accepted implementation plan and its provider-neutral and governed-write amendments, decisions and acceptance records; W0/W1 acceptance; frozen product layout; accepted A1–A15 and W1 backend-contract tuple.

The compatibility trace covered, in particular:

- `W2-QueryPlanningDesign.md:62-208`, the proposed leaf, relational and result algebra and inherited-form mapping;
- `W2-QueryPlanningDesign.md:210-288`, canonical root and validation ordering;
- `W2-QueryPlanningDesign.md:290-371`, lowering, row assembly, footprints, registries and refusals;
- `W2-QueryPlanningDesign.md:373-436`, future verification and ownership handoff;
- `docs/adr/A2-backend-contract.md:3-25`;
- `src/garns/backends/contracts/semantic.py:11-175`;
- `tests/contracts/test_contracts.py:122-195`;
- `src/garns/ir.py:177-492`;
- `src/garns/types.py:33-114`;
- `src/garns/calls.py:16-57`;
- `src/garns/resolve_read.py:560-789`;
- `src/garns/lower_sqlite.py:46-70`, `147-315`, `383-599`;
- `src/garns/engine.py:281-355`;
- `src/garns/footprint.py:49-223`;
- `corpus/conformance/worlds/sales/parity.garns:7-28`;
- `tests/test_static_dynamic.py:25-103`;
- the engine, storage, live, generation and inherited test files pinned by the source manifest.

No build, test, database, service, write, helper agent or Git operation was used.

## 1. Findings

### [P2-1] The W1 `ResultShape` projection loses hidden row keys required by inherited result semantics

**Classification:** bounded.

**Location:** `W2-QueryPlanningDesign.md:158-179`, especially the statement at lines 168-170 that the richer result specification projects losslessly to W1 using “one `ResultField` per visible field” and `key=True` exactly for key fields.

**Violated invariant:** The design brief requires a concrete, lossless connection to W1 `ResultShape` while accounting for identity, grouping and result cardinality (`W2-DesignExecutionBrief.md:57-71`). Inherited execution keeps row keys separately from visible result columns: ordinary rows receive hidden subject identity, grouped rows receive hidden group paths, and distinct rows use visible projected columns (`lower_sqlite.py:543-569`; `engine.py:292-303`). Those keys drive nested association and live keyed changes.

**Reproduction:** Consider an inherited ordinary query whose show list omits identity, such as a non-distinct query showing only `customer.name`, or the same shape as `sales_static.distinct_open_customers` with `distinct` removed. The proposed `ResultSpec.key` is subject identity under lines 158-162, but the visible fields contain only `customer`. Under lines 168-170, W1 receives only the visible `customer` `ResultField`; there is no identity field on which to set `key=True`. The same failure occurs when a grouped query groups by a path not included in its visible projection: `ResultSpec.key` contains the group path, but W1 receives no corresponding field. By contrast, inherited lowering explicitly selects `$k0`/`$kN` hidden keys and keeps them out of returned rows.

The nested-owner marker does not solve this: it defines a special owner field only for nested collections, not hidden root/group keys.

**Impact:** The asserted mapping is not lossless. An implementation must either omit the key, falsely mark an unrelated visible field, expose a previously hidden key, or invent an undocumented W1 convention. These choices change result shape, nested correlation or live delta identity and cannot satisfy the promised SQLite/result parity.

**Required correction:** Define the W1 representation of every structural key explicitly. The design must say whether hidden identity/group key fields are admitted in `ResultShape.fields`, give their stable qualified names and exact `SemanticType`, distinguish them from visible output, and specify how row assembly suppresses them from user rows while retaining them for keying. If W1 `ResultShape` cannot represent hidden fields without treating every field as visible, identify that as a W1 contract gap requiring amendment rather than claiming a lossless projection.

**Closure test:** Add structural design vectors for:

1. an ordinary collection that omits identity from `show`;
2. an optional/windowed result that omits identity;
3. a grouped result whose group key is not visible;
4. a distinct result whose visible fields are its keys;
5. a nested result requiring root-parent correlation.

For each, assert the exact `ResultSpec`, exact W1 `ResultShape`, visible returned columns and structural key tuple, and verify that encode/decode plus SQLite assembly preserves inherited rows and keys without exposing hidden fields.

### [P2-2] The advertised closed node algebra references undefined and contradictory value forms

**Classification:** bounded.

**Location:** `W2-QueryPlanningDesign.md:71-100`, `:104-135`, `:181-200`, `:210-245`, and `:355-364`.

**Violated invariant:** The brief requires immutable nodes with every field and invariant specified, exact closed registries, canonical encoding and exhaustive consumers (`W2-DesignExecutionBrief.md:57-70`, `:90-94`). A2 likewise makes exhaustive nodes and visitors the W2 closure condition (`A2-backend-contract.md:18-25`).

**Reproduction:** Attempt to derive the proposed `nodes.py` dataclasses and codec schema solely from the design:

- `Sort` refers to `Order` and `TieBreak` at line 117, but neither type has fields, variants, invariants or a registry definition.
- `ParameterDefault(name, Literal)` at line 186 and `AuthorityRequirement(...)` at line 198 enter the canonical top-level payload, but neither value has a defined schema, allowed multiplicity, uniqueness rule or validation invariant.
- `PlanPath` is introduced at lines 73-79 as the detached semantic path form, but expression and result fields are subsequently typed as inherited `I.PathRef` at lines 81-90 and 143-150. The inherited `PathRef` includes source `text` and `Loc` (`ir.py:219-225`), while the canonical representation says those fields are absent. The design never states whether decoded plan objects contain `PlanPath`, reconstructed `I.PathRef`, or both, nor which registry owns the encoded path tag.
- The top-level payload at lines 218-221 includes these values outside the stated four registries at lines 355-360. Consequently the “exact handler set” comparison cannot establish completeness for all canonical forms.

There is no unique implementation of the codec, validator, equality or exhaustive visitor tests from this specification. Two conforming implementers can choose incompatible encodings and object models while each claiming adherence.

**Impact:** The canonical digest and format registry are underdetermined, unknown-form refusal cannot be shown exhaustive, and the design’s own node-addition/handler-set tests are not satisfiable as written. This is a compatibility defect because persisted `garns.plan/1` bytes produced under one interpretation need not decode under another.

**Required correction:** Add a complete closed value schema alongside `RelNode` and `ResultItem`:

- define `Order`, every `TieBreak` variant, `ParameterDefault` and `AuthorityRequirement`;
- state exact field types, enum members, normalization, uniqueness and ordering rules;
- choose one detached path representation and specify precisely how it relates to inherited `I.PathRef` without admitting source spelling or `Loc` into canonical meaning;
- include every canonical leaf/metadata form in named registries consumed by encoder, decoder and validator;
- state which forms are DAG nodes and which are inline values.

**Closure test:** A schema-completeness test must enumerate every field annotation reachable from the canonical top object and prove it resolves to a primitive, exact enum, registered inline value, registered expression form or registered DAG node. Adding or renaming any reachable type must fail encoder, decoder and validator completeness tests. Golden vectors must also prove that changing source `text` or `Loc` leaves bytes unchanged while changing any semantic path/order/tie/default/authority field changes the digest or refuses.

### [P2-3] `FunctionUse.semantic_revision` has no defined source or canonical derivation

**Classification:** bounded.

**Location:** `W2-QueryPlanningDesign.md:92-100`, `:223-246`, `:274-280`, and `:357-364`; inherited registry at `src/garns/calls.py:16-57`.

**Violated invariant:** The design promises exact function identity and semantics, deterministic canonical encoding, revision-mismatch refusal before lowering, and independent dialect mappings without putting SQL templates in the root. Those promises must agree with the actual inherited registry.

**Reproduction:** The proposed `FunctionUse` requires `semantic_revision`, and validators must reject a revision mismatch. The inherited `Signature` contains only `qid`, parameter classes, result descriptor, SQL template and purity; it has no semantic revision. The design does not define whether `semantic_revision` is:

- an authored constant not currently present;
- a digest of the signature;
- a registry-wide digest;
- or a digest containing the SQLite `sql` template.

Including `Signature.sql` would make the supposedly backend-neutral semantic root depend on SQLite implementation text and conflict with lines 94-100. Excluding it still requires an exact canonical projection and versioning rule, which is absent. An arbitrary constant cannot detect a registry semantic change.

**Impact:** The bridge cannot populate this required field deterministically from the pinned inherited registry, and the decoder/lowerer cannot implement the promised semantic-mismatch refusal. Function-call plan bytes and cache invalidation would vary by unstated implementation choice, or semantic registry changes could reuse stale plans silently.

**Required correction:** Define an exact semantic fingerprint algorithm over backend-neutral registry fields, including normalization and handling of `"same"` result semantics, while explicitly excluding dialect SQL. State whether revisions are per-function or registry-wide, how dialect implementation tables bind to them, and which change classes require a new plan-format version versus a new semantic revision.

**Closure test:** Provide golden fingerprints for every current pure registry entry. Mutating qid, purity, arity, accepted parameter class, result rule or `"same"` behavior must change/refuse the revision; changing only a dialect SQL implementation must not alter the backend-neutral plan digest but must be caught by the dialect implementation/version gate. Unknown, volatile, effectful and stale-revision calls must refuse before SQL construction or adapter invocation.

## 2. Invariant analysis

Several attacks did not produce findings:

- The design explicitly depends on accepted A2 rather than relying on transitive W1 handoff, matching the accepted provider-neutral amendment.
- It preserves the accepted governed-write scope and does not revive W6 external capture.
- The proposed dependency graph is directionally consistent: compiler bridge imports the plan, backend lowerers import the plan, and the backend does not import parser/resolver/bridge code.
- The root excludes runtime authority, granted scope, secrets, physical-name defaults, SQL and driver objects. Authority requirements are described as preconditions rather than claims, preserving W1 runtime ownership.
- Query-only expressive constructs are not projected onto questions. The listed question refusals agree with resolver and footprint behavior for clock, static scalar algebra, calls, aggregates, `having`, `distinct`, static composition and windowed composition.
- The design correctly recognizes that current live execution still stores `I.Read` and that engine/live/legacy-lowerer integration lies outside W2’s frozen ownership. It does not treat a diagram as authorization.
- The inherited relational forms, expression variants, show variants, defaults, type dimensions, archive/scope/by behavior, composition closure, totals and nested lowering are substantially inventoried.
- Authored physical mapping and identifier quoting remain separate from semantic plan identities; no synthesized physical-name default is authorized.
- The validation order keeps static capability, binding, runtime authority and parameter checks before dialect I/O/effects, and does not let pure compilation issue authority.
- The nested owner convention is unusual but not itself inconsistent with the accepted W1 bytes: `ResultShape` requires only that each `NestedResult.owner_qualified_name` name a `ResultField`, and `SemanticType` admits the stated immutable marker. The design explicitly confines it to a non-scalar structural marker and asks for review. The blocking defect is instead the missing treatment of other hidden structural fields described in P2-1.
- The implementation and evidence plan distinguishes differential baselines from independent expected rows and accurately disclaims PostgreSQL, async, restart, concurrency and delivery proof.

## 3. Risks and next action

The residual risk below the finding bar is that canonical JSON details such as string normalization and numeric spelling will require careful golden vectors. The current inherited source literals are sufficiently constrained that this does not independently block once the closed value schema in P2-2 is supplied.

The single next action is one bounded design-document correction addressing P2-1 through P2-3, followed by a focused Consistency re-review on a newly pinned manifest. No source, W1 contract or ownership mutation is implied unless resolution of P2-1 determines that W1 cannot encode hidden structural result fields.
