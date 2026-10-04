# W2 shared query-planning design — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`; final corrected design draft, originating round-2 focused closure review, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by the thirteen-entry `dev-docs/W2-Design-MANIFEST-3.sha256` at SHA-256 `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`. The preserved preceding object is `dev-docs/W2-QueryPlanningDesign-Revision2.md` at SHA-256 `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`. Sources were read directly from the manifested filesystem tuple under the accepted no-Git exception.  
**Date:** 2026-10-03  
**Axis:** Consistency — focused originating verification of the bare-plan admission bypass and impossible resource-boundary witness, plus preservation of earlier closure proofs. Independent, adversarial, read-only. Nothing here relies on a current fresh peer or closure report. Filed verbatim by the lane owner.

**Verdict: GO** — both originating round-2 P2 findings are closed, all three initial Consistency closures remain preserved, and no new P0/P1/P2/P3 or architectural root was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on final design | Status |
|---|---|---|---|
| Consistency-2 P2-1 | Require an exact-instance admitted handle at every executable backend seam; remove bare-`Plan` compatibility paths; make the W1 protocol amendment an unenacted prerequisite. | Re-ran the original bypass through execute, consistent snapshot, subscribe and refresh. Final section 5.3 requires all executable W1 operations to accept only `AdmittedPlanHandle`; forbids bare-`Plan` overloads, public unwrap and compatibility fallback; binds each backend to a non-caller-replaceable verifier; and requires verifier resolution immediately before the private lowering path. Raw, extracted, copied, fabricated, cross-runtime, stale-generation, closed-runtime and pre-reopen values all have specified pre-lowering refusal paths. | **CLOSED** |
| Consistency-2 P2-2 | Replace the impossible 200,000-edge witness with a cross-limit audit, reachable-limit classifications and satisfiable interaction/precedence evidence. | Re-ran the original size lower bound. The final profile removes the 200,000/200,001 witness, derives a 10,256-reference guard from the closed unary relational algebra, explicitly permits the 8 MiB payload ceiling to dominate it, and no longer demands an impossible isolated exact-maximum plan. Independently reachable dimensions retain isolated exact/plus-one tests; dominated, registry, aggregate and payload-intersecting limits receive distinct satisfiable proof obligations. | **CLOSED** |
| Initial Consistency P2-1 | Preserve exact hidden structural key/role semantics and require a reviewed W1 result-shape amendment. | The Revision-2-to-final diff does not alter sections 3.3 or 4. Structural aliases, five result vectors, current-W1 refusal behavior and the amendment prerequisite remain intact. Final section 12 still declares both W1 prerequisites unenacted. | **REMAINS CLOSED** |
| Initial Consistency P2-2 | Preserve the closed canonical value/path schema and exhaustive registries. | The final change leaves the section 3.1 schemas and section 5.1 closure rules unchanged. The sole path model remains reconstructed `I.PathRef`; all canonical forms remain assigned to the six registries with no fallback schema. | **REMAINS CLOSED** |
| Initial Consistency P2-3 | Preserve deterministic backend-neutral function fingerprints and dialect-version separation. | The final change leaves the fingerprint algorithm, all nine golden hashes, semantic mutation rules and SQL-only dialect versioning unchanged. | **REMAINS CLOSED** |

## Changed-range analysis

`diff -u dev-docs/W2-QueryPlanningDesign-Revision2.md dev-docs/W2-QueryPlanningDesign.md` showed one consolidated correction confined to the accepted final remediation:

- section 5.2 replaces the flat resource-limit table and impossible universal exact-maximum requirement with explicit boundary classes, the closed-algebra 10,256-reference derivation, and class-specific evidence rules;
- section 5.3 replaces the proof-stripping `AdmittedPlan` wrapper with `AdmittedPlanHandle`, `PlanAdmissionRegistry` and a backend-bound `PlanAdmissionVerifier`;
- the validation pipeline now issues a handle and resolves it at backend entry before capability validation, parameter binding, lowering or adapter I/O;
- question execution, snapshot, subscription, refresh, nested-child and total-statement paths are explicitly covered;
- mixed-version migration requires `plan_admission_v1`, with old bare-plan entry points refusing while the new seam is introduced;
- future tests and the ownership table now exercise and require the same enforcement;
- the final prerequisite names one separately reviewed W1 amendment covering result roles and the admitted-handle/verifier protocol.

No change falls outside the accepted dispositions. The earlier result-shape, canonical-schema, function-fingerprint, inherited-ordering, query/question and governed-write decisions are preserved. No new architectural or bounded root was found. This was the second and final architectural correction; the review found no condition requiring the lane to stop under the architecture cap.

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-3.sha256` returned exactly `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`.
- All thirteen entries in `W2-Design-MANIFEST-3.sha256` verified.
- Recursive verification passed all 48 source inputs, all 13 control inputs and all 26 accepted W1 entries.
- Inventory counts remained exactly 13, 48, 13 and 26.
- The final design, preserved Revision 2, DRAFT-3 and RemPlan-2 hashes were respectively `0b8b77a0…af44e`, `db8a802f…67074`, `4562fccb…548f` and `8141d0e5…be13`.
- No tuple movement occurred.

I read the final design, `W2-Design-DRAFT-3.md`, `W2-Design-RemPlan-2.md`, and the complete Revision-2-to-final diff. I re-traced the original counterexamples against:

- final design section 5.2, resource-profile classifications and boundary evidence;
- section 5.3, runtime registry, exact-instance handle, bound verifier, lifecycle invalidation and migration ordering;
- section 6, the revised admission/authority/capability pipeline;
- sections 8 and 10, live-handle retention, consumer enumeration and bypass vectors;
- section 11, the explicit W1 protocol/ownership prerequisite;
- section 12, implementation nonclaims;
- accepted W1 `Plan` construction and backend plan-consuming signatures in `semantic.py:123-175` and `protocols.py:30-75`.

No current fresh peer report or originating closure report was read. No implementation test, build, database, service, helper, file write or Git/GWZ operation was used.

## 2. Invariant analysis

### Bare-plan bypass attack

The prior design rebuilt and compared semantics but discarded admission evidence before calling an unchanged raw-`Plan` backend interface. The final design closes each element of that sequence:

- The W1 amendment must change execute, consistent snapshot and subscribe to accept a handle, never a `Plan`.
- The handle is exact-instance, opaque, noncopyable, nonserializable and registry-issued only after complete rebuild-and-compare.
- Its private record binds the full plan, exact runtime identity, epoch, binding, lifecycle state and complete provenance key.
- Backend objects receive one verifier at construction; callers cannot choose or replace it per operation.
- The backend resolves the handle through that verifier before entering its non-public lowering path.
- Raw or extracted plans cannot substitute for handles, and lookalikes or handles from another registry fail identity resolution.
- Runtime close, migration, generation change and reopen revoke prior records or move to a distinct runtime/epoch.
- Snapshot, subscription and refresh retain the same handle. Nested and total statements remain internal products of an already verified operation rather than independent plan consumers.
- Static consumer enumeration fails on any new lowering or adapter path that accepts `Plan` or omits verifier resolution.
- Mixed versions fail their `plan_admission_v1` handshake; migration never enables admitted semantics while an executable bare-plan route remains.

The required W1 change is clearly a prerequisite, not an enacted amendment or implementation claim. Under current W1 bytes the design remains non-executable, so it does not falsely claim the bypass is already fixed in source.

### Impossible resource-witness attack

The original counterexample established that 200,000 64-character node references require at least 12.8 MB before JSON overhead, exceeding the 8 MiB payload limit. The final design no longer asserts that witness:

- The closed relational algebra has unary input edges and no arbitrary child-reference array.
- With 10,000 unique relational nodes, at most 9,999 unary input references are possible; one top-level root and 256 subplan roots yield the stated derived guard of 10,256 references.
- The guard is expressly classified as derived/dominated, and payload refusal is allowed to win.
- Its evidence is closed-schema arithmetic plus a reachable precedence interaction, not an impossible plan at the counter boundary.
- Only independently reachable limits require a valid exact-max witness with every other limit satisfied.
- Semantic-registry, payload-intersecting, outer/aggregate and dominated limits receive evidence appropriate to their actual reachability.
- The verification plan now asks for classified resource vectors, dominated-limit interactions, the closed-schema edge proof and maximal legal DAG reuse.

The revised obligations are internally satisfiable and permit deterministic cross-reader refusal precedence without pretending all numeric ceilings are independently reachable.

### Preserved attacks that failed

- Hidden ordinary/group/nested structural keys remain blocked under current W1 bytes rather than exposed or silently omitted.
- Canonical paths still omit source spelling and locations while preserving every semantic field.
- Function fingerprints remain reproducible and independent of dialect SQL.
- Runtime authority remains distinct from semantic admission: the bridge issues no handle or authority; runtime owns admission; backend verifies but does not mint trust.
- Backend/compiler dependency direction remains intact because the verifier is a contract-only foundation supplied by runtime; the backend imports neither runtime nor compiler.
- Static unsupported capability, parameter validation, lowering and adapter I/O remain downstream of admission.
- External capture, PostgreSQL proof, real async/runtime behavior, W3 public names and Surface review remain deferred rather than implicitly accepted.
- The final text does not authorize W1, runtime, legacy integration or implementation writes.

## 3. Risks and next action

Implementation could still incorrectly expose an unwrap, retain a bare-plan overload, misbind a verifier, or miscalculate a resource counter, but those are future code-review risks with explicit falsifiable design tests, not defects in this design object.

The single next action implied by this GO is to combine it with the required fresh full-design reviews and other originating closure testimony on the same manifest. If the design is accepted, implementation remains blocked until a separately scoped and independently reviewed W1 amendment adds structural result roles and the admitted-handle/verifier protocol, followed by an execution brief assigning runtime registry, backend verification and legacy wiring ownership.
