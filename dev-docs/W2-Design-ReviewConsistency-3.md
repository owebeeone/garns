# W2 shared query-planning design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`; final corrected design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by the thirteen-entry `dev-docs/W2-Design-MANIFEST-3.sha256` at SHA-256 `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`. Sources and controls were read directly from the manifested filesystem tuple under the accepted no-Git exception; no Git snapshot, commit, or cleanliness claim was used.  
**Date:** 2026-10-03  
**Axis:** Consistency — internal coherence, agreement with the complete controlling graph and inherited behavior, exact remediation closure, and satisfiability of the design’s evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — no P0, P1, P2, or P3 findings. The design is coherent as a design-only object. Its stated W1 structural-result-role and admitted-handle/verifier amendments remain explicit prerequisites and are not accepted or enacted by this verdict.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Initial Consistency P2-1 | Define structural identity/group/parent keys and require a reviewed W1 result-role amendment where current `ResultShape` is insufficient. | Re-traced ordinary, optional/windowed, hidden-group, distinct, and nested vectors through sections 3.3, 10, 11, and 12. The design gives exact structural aliases and assembly behavior, refuses affected W1 projection under current bytes, and treats the amendment as a prerequisite rather than an accomplished change. | **CLOSED** |
| Initial Consistency P2-2 | Close every canonical leaf/value schema and registry and select one path representation. | Re-traced `TypeRef`, paths, terminals, `Order`, `TieBreak`, defaults, authority requirements, subplans, function uses, result forms, and top-level fields through sections 3.1 and 5.1. One reconstructed existing `I.PathRef` model is specified, source spelling and `Loc` are excluded from canonical meaning, and six exact registries plus recursive schema-closure checks cover all reachable forms. | **CLOSED** |
| Initial Consistency P2-3 | Define backend-neutral function fingerprints and separate dialect implementation versioning. | Re-traced the stated fingerprint inputs against the pinned function registry. The algorithm covers qid, purity, ordered parameter classes, builtin and `same` result semantics; SQL is excluded and governed by a separate dialect implementation-version gate. The nine current pure-function goldens remain specified. | **CLOSED** |
| Initial Safety P2-1 | Bind canonical integrity to trusted semantic provenance through deterministic rebuild-and-compare. | Re-traced correctly digested same-origin scope, authority, archive, member, identity, predicate, result, subplan, and relabeling mutants through final sections 5.3, 6, 9, 10, and 11. Full-envelope and recursive-closure equality is required before handle issuance, and provenance remains distinct from binding, authority, and capability checks. | **CLOSED** |
| Initial Safety P2-2 | Define a versioned hostile-input resource profile with deterministic counting and refusal precedence. | Re-traced payload, encoding, nesting, strings, identifiers, nodes, references, expressions, subplans, results, functions, parameters, combined depth, and aggregate-work cases through final section 5.2. Counters and precedence are explicit; unreachable or intersecting ceilings are no longer falsely required to have isolated plus-one witnesses. | **CLOSED** |
| Round-2 Consistency P2-1 | Preserve admission evidence through every executable backend seam using an opaque exact-instance handle and bound verifier. | Re-ran the raw-plan bypass sequence against final sections 5.3, 6, 9, 10, and 11. `execute`, `consistent_snapshot`, `subscribe`, and refresh are specified to accept/pass handles only; backend entry resolves through a construction-bound verifier; no bare-`Plan` overload, public unwrap, or compatibility fallback is allowed. Raw, extracted, copied, fabricated, cross-runtime, cross-binding, stale-generation, closed-runtime, and pre-reopen cases all have explicit pre-lowering refusal obligations. | **CLOSED** |
| Round-2 Safety P2-1 | Apply the same enforceable boundary to mixed-version, lifecycle, nested, total, snapshot, subscription, and refresh paths. | Re-traced partial-migration and stale-caller paths. The final design requires `plan_admission_v1`, refuses mixed versions at open, revokes registry records before close/migration publication, carries the same handle through live lifecycle paths, keeps derived child/total statements inside a verified operation, and requires static consumer enumeration. | **CLOSED** |
| Round-2 Consistency P2-2 | Replace the impossible 200,000-edge witness and audit interactions among resource ceilings. | Re-traced the original fixed-width-reference counterexample through final lines 357–408. The design now derives the 10,256 reference guard from the closed unary relational algebra and 256 subplan roots, classifies it as dominated, requires closed-schema arithmetic and payload-precedence evidence instead of an impossible isolated maximum, and removes the illegal arbitrary-fanout vector. | **CLOSED** |

## Changed-range analysis

The preserved initial design has 459 lines, the preserved revision-2 design has 650 lines, and the final design has 711 lines.

The initial-to-revision-2 changes were confined to the first remediation’s accepted dispositions:

- one reconstructed semantic path model and a closed inline-value schema;
- deterministic function fingerprints and dialect-version separation;
- explicit hidden structural result roles and five normative result vectors;
- `garns.plan-limits/1`;
- trusted full-envelope rebuild-and-compare admission;
- corresponding verification and ownership prerequisites.

The revision-2-to-final changes are confined to the second remediation:

- resource ceilings are classified as independently reachable, semantic-registry, derived/dominated, payload-intersecting, or aggregate;
- the impossible 200,000-reference witness is replaced by closed-algebra arithmetic for the 10,256 derived guard and satisfiable interaction/precedence evidence;
- the runtime-internal wrapper that previously stripped proof is replaced by an exact-instance `AdmittedPlanHandle`, process-local admission registry, and backend-bound `PlanAdmissionVerifier`;
- lifecycle epoch, runtime identity, binding, generation, cache, close/reopen, and migration invalidation rules are explicit;
- execute, consistent snapshot, subscription, refresh, nested, and total paths are covered;
- mixed-version migration ordering fails closed and requires `plan_admission_v1`;
- the verification plan attacks every bypass and requires exhaustive executable-consumer enumeration;
- the ownership table and final nonclaims identify both required W1 amendments as prerequisites.

No changed range silently modifies the grammar, accepted W1 bytes, source implementation, public API, query/question split, authored-storage rules, governed-write scope, external-capture deferral, PostgreSQL/async claims, or frozen ownership. No new architectural root was found. Both architecture remediation allowances are nevertheless consumed as recorded; this GO does not reset that history.

## 0. Evidence base

At both review boundaries:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-3.sha256` returned exactly `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`.
- `shasum -a 256 dev-docs/W2-QueryPlanningDesign.md` returned exactly `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`.
- `shasum -a 256 -c dev-docs/W2-Design-MANIFEST-3.sha256` passed all thirteen entries.
- Recursive verification passed all 48 entries in `W2-DesignSourceInputs.sha256`, all 13 entries in `W2-DesignControlInputs.sha256`, and all 26 entries in `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`.
- Inventory counts remained exactly 13, 48, 13, and 26. No tuple movement occurred.

I read the complete:

- workspace and product instructions;
- current program checkpoint;
- review-loop skill and canonical report template;
- W2 execution brief;
- final 711-line design;
- preserved 459-line initial design and 650-line revision-2 design;
- `W2-Design-DRAFT.md`, `W2-Design-DRAFT-2.md`, and `W2-Design-DRAFT-3.md`;
- both remediation plans;
- both initial review reports and both fresh round-2 review reports;
- accepted implementation plan, provider-neutral amendment and acceptance, operator decisions, governed-write amendment and acceptance, W0/W1 acceptance, and frozen product layout;
- accepted A1–A15 and complete W1 contract tuple;
- relevant pinned IR, type, function-registry, storage, SQLite lowering, engine, live, footprint, generation, and test sources.

The focused consistency trace covered:

- final design lines 62–280: closed leaf, relational, result, inherited-read, expression, default, type, cardinality, ordering, identity, nested, total, and composition mappings;
- lines 282–408: canonical root, exact schema, resource profile, refusal precedence, and satisfiable evidence classifications;
- lines 410–518: semantic provenance, handle/verifier seam, lifecycle invalidation, migration ordering, validation, capability, parameter, and authority order;
- lines 520–600: SQLite lowering, result assembly, question-only footprints, shared-plan reuse, registries, and refusal catalog;
- lines 602–711: ordered verification, legacy integration ownership, W1 amendment prerequisites, evidence, and nonclaims;
- `src/garns/backends/contracts/semantic.py:11-175`;
- `src/garns/backends/contracts/protocols.py:30-75`;
- `docs/adr/A2-backend-contract.md:3-25`;
- `docs/adr/A3-async-lifecycle.md`, A6, A9, A11–A15;
- `src/garns/ir.py:177-490`;
- `src/garns/types.py:30-114`;
- `src/garns/calls.py:16-57`;
- `src/garns/resolve_read.py:590-789`;
- `src/garns/storage.py:63-302`;
- `src/garns/lower_sqlite.py:28-70,383-599`;
- `src/garns/engine.py:183-355`;
- `src/garns/footprint.py:45-223`;
- `src/garns/live.py:95-254`;
- the manifested inherited tests and evidence inventory.

I compared initial to revision 2 and revision 2 to final with read-only unified diffs. No build, test, database, service, dependency, helper agent, file write, Git, or GWZ operation was used.

## 2. Invariant analysis

The following adversarial attacks did not produce findings:

- **W1 prerequisite coherence:** Current W1 `ResultShape` cannot represent all required hidden structural roles, and current protocols accept bare `Plan`. The final design does not claim otherwise. It specifies the required amendment semantics, refuses affected execution until acceptance and integration, and keeps both amendments outside current authority.
- **Admission-boundary completeness:** The handle is exact-instance, noncopyable, nonserializable, and resolved only by a verifier bound at backend construction to the same runtime registry. The private record retains the plan, runtime identity, epoch, binding, provenance key, and lifecycle state. This closes proof stripping without reversing compiler/backend dependencies.
- **Mixed-version behavior:** The migration sequence never permits reliance on admission while an executable bare-plan route remains. Old entries refuse, protocol negotiation is mandatory, and W2 plans remain disabled until consumer enumeration and bypass evidence pass.
- **Lifecycle coherence:** Close marks records closed before backend/pool close; reopen creates a new runtime identity and registry; migration revokes the old binding set before publishing the new one. Byte-identical old handles therefore remain invalid.
- **Result-shape consistency:** Structural aliases remain distinct from visible aliases, exact W1 limitations are acknowledged, and ordinary, optional/windowed, grouped, distinct, and nested shapes have compatible key and assembly rules.
- **Canonical closure:** Every reachable value belongs to a named registry or primitive/enum terminal, unknown fields and tags refuse, DAG reachability and acyclicity are mandatory, and source locations or spelling cannot change canonical meaning.
- **Resource evidence:** The final classification distinguishes semantic admission limits from outer safety ceilings and dominated guards. It no longer promises mutually impossible exact-boundary witnesses.
- **Function identity:** Backend-neutral semantic fingerprints cover registry meaning while dialect SQL remains independently versioned. This preserves plan identity without importing SQLite implementation text.
- **Inherited semantic breadth:** Every inherited `Read`, `ShowTerm`, `Operand`, and `Expr` form is mapped or retains an evidenced question-only refusal. Query expressiveness is not narrowed to satisfy live restrictions.
- **Ordering and cardinality:** Ordinary and grouped tie behavior, distinct non-ordering, rank, paging totals, optional-single checks, global aggregates, nested correlation, and `last N` selection/emission agree with the cited inherited lowerer.
- **Authority separation:** The root contains requirements, not grants. Rebuild-and-compare issues no caller authority, and runtime trusted-context checks remain separate from plan admission, capability, binding, and parameter validation.
- **Physical provenance and injection resistance:** Logical identities resolve only through authored mappings; identifiers are quoted and all caller/default/scope/clock/parent values are bound.
- **Ownership and scope:** The design names exact W2-owned paths and exact external integration gaps. It does not treat its diagrams or future test plan as authority to modify engine, live, legacy lowering, generation, W1 contracts, or public surfaces.
- **Deferrals:** External capture, cryptographic/provider integration, PostgreSQL execution, real async workers, crash/restart proof, public naming, and W3 Surface remain deferred without weakening the design’s semantic and ownership obligations.
- **Evidence honesty:** Differential SQLite evidence is a comparison baseline rather than the sole oracle, and the document accurately states what future tests cannot prove.

## 3. Risks and next action

Residual risk remains in the future implementation of canonical encoding, resource witnesses, registry lifecycle, SQLite parity, and the exact accepted shape of the two W1 amendments. Those are explicit implementation or prerequisite-review risks, not contradictions in this design.

The single next action is manager acceptance of this design-only tuple, followed—before any executable W2 integration—by a separately scoped and independently reviewed W1 amendment covering structural result roles and the admitted-handle/verifier protocol, then an execution brief assigning runtime registry/admission and legacy wiring ownership. This GO does not authorize those amendments, implementation, source writes, or acceptance of future evidence.
