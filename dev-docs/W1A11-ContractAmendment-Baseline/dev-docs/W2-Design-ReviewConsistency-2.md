# W2 shared query-planning design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`; corrected design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by the nine-entry `dev-docs/W2-Design-MANIFEST-2.sha256` at SHA-256 `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`. Sources were read directly from the manifested filesystem tuple under the accepted no-Git exception; no Git snapshot or cleanliness claim was used.  
**Date:** 2026-10-03  
**Axis:** Consistency — internal coherence, agreement with controlling contracts and inherited behavior, exact remediation closure, and satisfiability of the design’s evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block: one architectural incomplete closure and one bounded specification/test contradiction. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Initial Consistency P2-1 | Add exact structural aliases, roles, result vectors, and declare a reviewed W1 result-shape amendment prerequisite. | Re-traced ordinary, optional/windowed, hidden-group, distinct, and nested cases through corrected sections 3.3, 10, 11 and 12. The design no longer claims current W1 bytes can losslessly represent hidden keys; affected W1 projections explicitly refuse pending amendment. | **CLOSED** |
| Initial Consistency P2-2 | Close canonical value schemas and registries; select reconstructed `I.PathRef` as the sole path model. | Re-traced every original undefined form. `Order`, `TieBreak`, defaults, authority requirements, subplans and function uses now have schemas; six registries and recursive schema-closure checks cover the top-level object; path spelling/location exclusion is explicit. | **CLOSED** |
| Initial Consistency P2-3 | Define backend-neutral function fingerprints and dialect-version separation. | Independently recomputed all nine listed pure-function fingerprints from the pinned registry using the stated compact sorted-key JSON plus newline algorithm; every value matched lines 124–132. SQL text is excluded and separately versioned. | **CLOSED** |
| Initial Safety P2-1 | Add runtime-owned deterministic rebuild-and-compare admission for the complete envelope and recursive closure. | Re-traced the original same-origin mutant through corrected sections 5.3, 6, 8, 10 and 11 and the accepted W1 backend protocols. The runtime comparison is specified, but the admitted wrapper is removed before the unchanged backend entry points consume the plan; direct W1 `Plan` consumption remains an unguarded route. | **OPEN — P2-1** |
| Initial Safety P2-2 | Add concrete `garns.plan-limits/1` values, counting, precedence and boundary vectors. | Re-traced the original breadth/fan-out counterexample. Limits and precedence are now concrete, but the required 200,000-edge exact-boundary witness cannot fit within the simultaneously mandatory 8,388,608-byte payload ceiling. | **OPEN — P2-2** |

## Changed-range analysis

The preserved initial object has 459 lines; the corrected object has 650. The material changes are confined to the five accepted remediation dispositions:

- lines 73–145 close the path/value schema and function-fingerprint gaps;
- lines 213–251 define hidden result keys, five normative vectors, and the W1 result-shape amendment prerequisite;
- lines 329–395 add closed-schema and resource-profile rules;
- lines 397–428 add trusted rebuild-and-compare admission;
- lines 430–595 and 604–650 propagate ordering, verification, ownership and launch prerequisites.

No unrelated scope expansion, grammar change, external-capture revival, PostgreSQL implementation claim, or source/contract mutation appears. The W1 result-shape amendment prerequisite is coherent with the design-only boundary: it blocks affected executable projection rather than pretending current W1 bytes already provide structural-field roles.

P2-1 is not a third or distinct architectural root. It is incomplete closure of the remediation plan’s existing architectural provenance root: the comparison exists, but the accepted W1 consumption boundary still accepts the unwrapped constructible value. P2-2 is bounded and text-fixable. One architectural remediation has been consumed; the ordinary cap leaves at most one further architectural remediation.

## 0. Evidence base

At both review boundaries:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-2.sha256` returned exactly `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`.
- `shasum -a 256 -c` passed all nine manifest entries.
- Recursive verification passed all 48 source inputs, all 13 control inputs, and all 26 accepted W1 manifest entries.
- Inventory counts were exactly 9, 48, 13 and 26. No tuple movement occurred.

I read the complete workspace and product instructions, current checkpoint, review-loop skill and canonical template; the full execution brief, initial and corrected designs, both draft testimonies, both initial reports, and merged remediation plan. I compared the initial and corrected designs with `diff -u`.

The controlling graph inspected included the complete accepted implementation plan, provider-neutral seam amendment and acceptance, governed-write scope amendment and acceptance, operator decisions, W0/W1 acceptance, frozen product layout, accepted A1–A15, and the W1 contracts. The compatibility trace particularly covered:

- corrected design lines 62–280: value, relational and result algebra and inherited-form mapping;
- lines 282–428: canonical root, closed schema, resource profile and semantic provenance;
- lines 430–545: validation order, lowering, result assembly, footprints, caching and refusal catalog;
- lines 546–650: future verification, ownership gaps, evidence and launch prerequisites;
- `src/garns/backends/contracts/semantic.py:62-175`;
- `src/garns/backends/contracts/protocols.py:30-75`;
- `docs/adr/A2-backend-contract.md:3-25`;
- `docs/adr/A11-trusted-context.md:3-41`;
- `src/garns/ir.py:37-43,177-390`;
- `src/garns/types.py:13-103`;
- `src/garns/calls.py:16-57`;
- `src/garns/resolve_read.py:590-789`;
- `src/garns/lower_sqlite.py:430-527`;
- `docs/PRODUCT_LAYOUT.md:6-20`.

A permitted pure in-memory Python command recomputed the nine function fingerprints from `calls.REGISTRY`; all matched. No files, Git state, database, service, dependency or implementation state were changed.

## 1. Findings

### [P2-1] Admission is discarded before the accepted W1 plan-consuming boundary

**Classification:** architectural incomplete closure.

**Location:** `W2-QueryPlanningDesign.md:397-428`, especially lines 409–415 and 422–428; pipeline at lines 432–445; cache/use statement at lines 513–519; ownership table at lines 610–616. Accepted W1 entry points remain `AsyncConnection.execute(plan: Plan, ...)`, `consistent_snapshot(plan: Plan, ...)`, and `AsyncBackend.subscribe(plan: Plan, ...)` at `src/garns/backends/contracts/protocols.py:30-75`. `Plan` and `FrozenPlanRoot` remain publicly constructible immutable values at `semantic.py:123-160`.

**Violated invariant:** corrected section 5.3 promises that serialized or caller-constructed plans cannot execute and that provenance comparison precedes every lowering/adapter path. A provenance guard must therefore survive to, or be re-established at, every accepted plan-consuming boundary. An earlier runtime convention is not equivalent when the accepted backend protocol still consumes the indistinguishable raw value.

**Reproduction/state sequence:**

1. Construct a canonical, correctly digested W1 `Plan` bearing a genuine binding origin and outer read identity but with a removed `ScopeFilter`, `AuthorityRequirement`, archive/member/identity filter, predicate, result expression, or recursive subplan.
2. Hold a genuine context accepted by the W1 authority boundary.
3. Bypass the proposed high-level `admit_plan` call and invoke the accepted `AsyncConnection.execute`, `consistent_snapshot`, or `AsyncBackend.subscribe` protocol directly with that raw `Plan`.
4. The design’s `AdmittedPlan` cannot protect this route: lines 411–415 explicitly make it non-W1 and unwrap it back to the exact raw `Plan` before calling the existing protocol.
5. The backend cannot reconstruct the expected plan itself under the stated dependency rules: it owns neither the resolved program nor the compiler bridge, and sections 2 and 10 prohibit backend imports of resolver/bridge code.
6. The forged but structurally valid plan therefore reaches the same accepted W1 plan-consumption signature as a rebuilt-equivalent plan without any type, token or protocol evidence that admission occurred.

This is the original semantic-provenance counterexample through the corrected call graph, not a demand for future implementation proof. The text promises a property that its unchanged controlling interface cannot enforce.

**Impact:** a backend implementation conforming to W1 and this design can accept raw caller-constructed semantics that bypass the sole rebuild-and-compare step. Scope, archive/member discrimination, identity predicates, result meaning and recursive composition can differ from the named read while retaining valid origin metadata. Implementers must either rely on an undocumented “only runtime calls this” convention or independently alter the W1/backend boundary.

**Required correction:** choose and specify one closed enforcement boundary:

- amend the W1 plan-consuming operations to require an opaque, runtime-issued admitted value whose validity cannot be stripped before backend consumption; or
- move/repeat admission at every backend operation that accepts a plan and give that boundary the exact trusted inputs necessary to rebuild/compare; or
- make the raw W1 operations demonstrably unreachable outside a wrapper that enforces admission, with the protocol and ownership amendment spelling out that restriction.

The correction must cover execute, snapshot and subscribe, preserve backend/compiler dependency direction, and explicitly supersede the current statement that the runtime unwraps to an indistinguishable raw `Plan`.

**Closure test:** with a genuine context and binding, invoke every plan-consuming operation through every reachable protocol path using correctly digested same-origin mutants for scope, authority, archive, member, identity, predicate, result and subplan changes. Every path must refuse `PLAN_PROVENANCE_MISMATCH` before capability validation, lowering or adapter invocation. The exact rebuilt plan must succeed. A test or architecture check must fail if any operation again accepts a raw constructible `Plan` without admission evidence.

### [P2-2] The resource profile requires an impossible exact-boundary edge witness

**Classification:** bounded.

**Location:** `W2-QueryPlanningDesign.md:357-395`, particularly payload maximum at line 364, edge maximum at line 369, and the requirements at lines 391–395 to accept every exact maximum and test 200,000 versus 200,001 references to one shared node. Future verification repeats these exact/plus-one obligations at lines 576–581.

**Violated invariant:** the design brief requires falsifiable verification. Each promised exact-limit witness must be representable while remaining within every other inclusive limit.

**Reproduction:**

1. Every relational/subplan edge is a reference to a content-addressed node id (`:295-297`), and each node id is 64 lowercase hexadecimal characters (`:101`).
2. A payload containing 200,000 edge occurrences therefore needs at least 12,800,000 bytes for the identifier characters alone.
3. JSON string quotes, separators, field names and the referenced nodes only increase that size.
4. The same profile rejects every payload over 8,388,608 bytes (`:364`).
5. Therefore no valid payload can accept exactly 200,000 edge references while staying within the payload maximum, contrary to lines 391–395. The requested 200,001 plus-one vector is likewise dominated by payload refusal rather than isolating the edge counter.

**Impact:** the resource profile and its mandatory test plan cannot both be implemented. One implementation may treat the edge threshold as intentionally unreachable; another may relax the payload ceiling or use a non-specified compressed/reference encoding. The required diagnostic-precedence and boundary evidence cannot establish the claimed interoperable admission contract.

**Required correction:** make every independently tested limit reachable under all other limits. For example, lower the edge maximum below the maximum representable count under the canonical payload ceiling, raise the payload ceiling consistently, or explicitly define dominated limits and replace impossible exact/plus-one obligations with reachable interaction/precedence vectors. Recheck every dimension for the same cross-limit reachability problem rather than correcting only the named number.

**Closure test:** construct a canonical witness at each advertised independently reachable maximum while all other counters remain below their maxima, then a plus-one witness that crosses only the intended counter and produces the specified refusal. Add a mechanical lower-bound check proving that fixed-width references and required JSON overhead fit beneath the payload ceiling for the chosen edge boundary.

## 2. Invariant analysis

The following adversarial attacks did not produce additional findings:

- **W1 result-shape prerequisite:** corrected lines 223–251 no longer silently redefine W1. They identify the missing visibility/structural role, give stable aliases and five vectors, refuse affected projection under current bytes, and require a separately scoped and reviewed amendment. This preserves design coherence and authority boundaries.
- **Closed canonical schema:** the six named registries, recursive annotation closure, unknown-field rejection, inline-versus-DAG distinction and reconstructed `I.PathRef` model close the initial ambiguity. Semantic fields are retained while source spelling and `Loc` remain noncanonical.
- **Function semantics:** the fingerprint algorithm is deterministic and backend-neutral. All nine golden hashes reproduce from the pinned registry. Changes to semantic identity affect plan admission, while dialect SQL changes remain under a separate implementation-version gate.
- **Inherited SQLite ordering:** the correction accurately follows `lower_sqlite.py:458-471`: ordinary non-distinct rows and requested grouped paths receive inherited tie-breaks; distinct rows do not gain an invented ordering. Nested `last N` matches the current descending selection and ascending emission behavior.
- **Query/question separation:** query-only expression capability is not narrowed by question footprint restrictions. Only questions derive footprints and live routing, while the same admitted plan is intended for initial and refresh computation.
- **Authority content:** canonical roots contain requirements rather than grants and exclude trusted contexts, effective scope, principals, writers, secrets and parameter values. Pure compilation does not mint authority.
- **Physical provenance:** authored `RelationMapping` remains the only source of physical identifiers; identifiers are quoted and values bound. No synthesized table/column default or schema dispatch appears.
- **Ownership:** the design names W2-owned paths and separately identifies legacy engine, live, footprint, lowerer, generator, W1 result-shape and runtime-admission gaps. It does not treat the diagram or design acceptance as implementation authority.
- **Scope amendments:** the document preserves governed-write-only release scope and does not revive W6, P6 or external capture. Cryptographic/provider integration, PostgreSQL execution, async workers, crash/restart proof, public naming and W3 Surface remain properly deferred.
- **Evidence honesty:** differential SQLite behavior is only a baseline, not the sole oracle. The design accurately disclaims PostgreSQL, real async, concurrency, restart, delivery and driver-codec proof.

## 3. Risks and next action

Canonical JSON implementation details, W1 role-amendment shape, real runtime ownership, and backend behavior remain future risks, but they are either explicitly gated or below the finding threshold here.

The single next action is one consolidated design correction that carries admission evidence through every accepted W1 plan-consumption path and makes the resource profile’s boundary obligations mutually satisfiable. Because P2-1 is the existing architectural provenance root incompletely closed, this consumes the remaining ordinary architectural remediation allowance rather than introducing a third root. The revised full design requires a fresh same-tuple Consistency/Safety review and originating counterexample verification before acceptance; no implementation or W1 amendment is authorized by this verdict.
