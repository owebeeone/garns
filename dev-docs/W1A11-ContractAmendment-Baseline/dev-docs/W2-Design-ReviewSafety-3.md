# W2 shared query-planning design — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`; final corrected design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by `dev-docs/W2-Design-MANIFEST-3.sha256` at SHA-256 `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`. Sources and controls were read directly from the manifested filesystem tuple under the accepted no-Git exception; no Git snapshot or cleanliness claim was used.  
**Date:** 2026-10-03  
**Axis:** Safety — degraded and mixed-version paths, irreversible transitions, disclosure, hostile-input bounds, stuck states, fail-closed behavior, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new architectural P2 finding blocks. Both remediation-2 findings and all five initial findings are closed at design level, but the two architectural remediation rounds are exhausted; P2-1 therefore stops the lane for operator redesign-or-accept direction rather than authorizing a third architecture correction.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Initial Consistency P2-1 — W1 result projection loses hidden structural keys | Add explicit structural roles and make a reviewed W1 result-shape amendment a prerequisite. | Current lines 213–251 retain exact aliases, visible/structural separation, five normative vectors, and refusal under current W1 bytes. Lines 674 and 706–711 preserve the amendment as a prerequisite rather than enacting it. | Closed for design coherence. |
| Initial Consistency P2-2 — canonical value algebra incomplete | Close the schema and use one reconstructed existing path model. | Lines 73–108 and 329–355 define the exact path/value model, six closed registries, schema-closure checks, unknown-field rejection, and semantic-versus-source-spelling vectors. | Closed. |
| Initial Consistency P2-3 — function semantic revision underived | Define deterministic backend-neutral fingerprints and separate dialect implementation versions. | Lines 110–145 retain the fingerprint input, nine goldens, mutation behavior, and independent dialect-version invalidation. | Closed. |
| Initial Safety P2-1 — canonical integrity mistaken for trusted provenance | Rebuild and compare the complete trusted semantic envelope before execution. | Lines 410–420 rebuild and compare noun, parameters/defaults, result, live bound, authority requirements, functions, complete DAG, subplans, origin, and outer values. Lines 476–482 retain the original mutant refusals. | Original counterexample closed. |
| Initial Safety P2-2 — hostile roots lack a concrete resource contract | Define a fixed versioned profile, bounded preparse, counting rules, precedence, and boundary vectors. | Lines 357–408 define `garns.plan-limits/1`, streaming limits, deterministic precedence, explicit stacks, boundary classes, and interaction vectors. | Closed, including the round-2 reachability correction. |
| Round-2 Consistency/Safety P2-1 — admission proof disappears at the bare-`Plan` backend seam | Require an exact-instance opaque handle and bound backend verifier at every executable entry; remove executable bare-plan compatibility. | Lines 422–465 require handle-only execute/snapshot/subscribe/refresh paths, a runtime-local registry, exact-identity lookup, bound verifier, lifecycle state, and static enumeration of every lowering/I/O consumer. Lines 467–474 define fail-closed migration and mixed-version handshake. | Original bypass sequence closed, subject to the distinct operation-lifetime root below. |
| Round-2 Consistency P2-2 — impossible 200,000-edge boundary witness | Classify dominated limits and replace impossible isolated vectors with arithmetic and precedence tests. | Lines 362–408 classify each ceiling, reduce relational/subplan references to the closed-algebra maximum of 10,256 occurrences, require mechanical minimum-encoding checks, and prohibit the impossible fan-out vector. | Closed. |

## Changed-range analysis

The complete diff from preserved `W2-QueryPlanningDesign-Revision2.md` to the current design changes two areas only:

1. **Resource-boundary evidence, lines 357–408.** Limits now have explicit reachability classes. The impossible 200,000-edge witness is replaced by a 10,256-occurrence derived guard, closed-schema arithmetic, and payload-precedence interaction evidence. This closes the bounded round-2 finding without widening authority or implementation scope.
2. **Admission boundary, lines 410–482 and corresponding pipeline/tests/ownership text.** The runtime-internal wrapper that previously unwrapped to a bare W1 `Plan` is replaced by a required W1 `AdmittedPlanHandle`/`PlanAdmissionVerifier` protocol amendment. The design now rejects raw plans, copied/fabricated handles, cross-runtime/binding/generation handles, closed-runtime handles, and mixed-version peers before lowering.

The changed admission range closes proof stripping at entry, but introduces a new lifecycle boundary: verifier success returns the private raw `Plan` to the backend and has no operation lease or quiescence obligation spanning subsequent lowering and adapter work. Registry revocation therefore does not fence a concurrently resolved operation. This is a **new architectural root cause**, not a recurrence of the raw-plan bypass and not a bounded textual ambiguity.

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-3.sha256` returned exactly `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`.
- `shasum -a 256 dev-docs/W2-QueryPlanningDesign.md` returned exactly `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`.
- The manifest contained exactly thirteen entries.
- `shasum -a 256 -c` passed for all thirteen top-level entries.
- Recursive verification passed for all 48 source/test/grammar entries, all 13 control entries, and all 26 accepted W1 entries.
- Inventory counts remained exactly 48, 13, and 26. No tuple movement occurred.

I read:

- `AGENTS_GWZ.md`, product `AGENTS.md`, and `CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical review template;
- the complete `W2-DesignExecutionBrief.md`;
- the complete current 711-line design, preserved initial design, and preserved revision-2 design;
- all three DRAFT testimonies, both remediation plans, and both complete initial and round-2 Consistency/Safety reports;
- every artifact in `W2-DesignControlInputs.sha256`, including the accepted parent plan, provider-neutral seam amendment and acceptance, governed-write amendment and acceptance, operator decisions, W0/W1 acceptances, W1 manifest, and frozen product layout;
- accepted A1–A15 and the complete manifested W1 contract tuple;
- the relevant manifested IR, type, function-registry, storage, lowering, engine, live, footprint, generation, and test sources.

Focused safety traces included:

- current canonical schema/resource profile: lines 282–408;
- admitted-handle and verifier lifecycle: lines 410–482;
- validation/authority/lowering sequence: lines 484–518;
- live handle reuse: lines 558–583;
- attack vectors and legacy ownership: lines 602–681;
- accepted A2 pre-effect validation requirement;
- accepted A3 graceful-drain/nonquiescent lifecycle;
- accepted A8 commit fence and worker containment;
- accepted A12 generation publication and mixed-version refusal;
- W1 protocol entries at `protocols.py:30-75`;
- initial-to-current and revision-2-to-current textual diffs.

No file, Git state, database, service, dependency, build, or process state was modified.

## 1. Findings

### [P2-1] Verifier resolution is not retained as an operation lease across revocation

**Classification:** new architectural root cause.

**Location:** `W2-QueryPlanningDesign.md:429-457`, especially the verifier resolving a handle and returning the private `Plan` at lines 435–441; lifecycle revocation at lines 449–456; operation reuse at lines 459–465; migration ordering at lines 467–474; pipeline at lines 486–502. Controlling lifecycle requirements are A2’s validation-before-every-effect rule, A3’s drain-before-closed rule, and A12’s generation/mixed-version fencing.

**Violated invariant:** closing a runtime or changing a binding generation must not permit an already-revoked admission to begin or continue backend work under stale plan/binding semantics. Admission validity must cover the whole executable operation until quiescence, not only the instant at which the backend obtains a raw plan.

**Reproduction/state sequence:**

1. Runtime `R`, binding generation `G`, and registry epoch `E` have a valid admitted handle `H`.
2. `execute(H, ...)` enters the backend. Its bound verifier checks that `H` is registered, `OPEN`, bound to `R/G/E`, and returns the private raw `Plan`, as specified at lines 435–440.
3. Pause the operation after verifier return but before static capability validation, lowering, adapter invocation, result fetch, or snapshot watermark completion.
4. Concurrent close or migration begins:
   - close marks records `CLOSED` and increments the epoch before pool/backend close; or
   - migration revokes the old binding set before publishing generation `G+1`.
5. The paused operation no longer carries a verifier-controlled object. It holds a raw plan, and the design defines neither:
   - an operation lease counted against registry/runtime quiescence;
   - a revocation fence held through lowering and adapter completion;
   - a second binding/epoch check immediately before each effect or snapshot publication; nor
   - a rule that migration/close waits for or returns typed nonquiescence for resolved plan operations.
6. The operation resumes and can lower or invoke the adapter using generation `G` after its admission record is closed or after `G+1` is published.
7. Static consumer enumeration does not catch this sequence: the entry did call the verifier. Exact-handle identity, cache invalidation, and mixed-version open handshake also do not retract the already-returned raw plan.

For a one-shot query this can return rows under a stale authored mapping or schema generation. For `consistent_snapshot` or refresh it can pair rows evaluated under the old admitted plan with lifecycle/generation state observed after migration, defeating A6’s exact `(rows,H)` snapshot claim or producing a late delivery after close. On SQLite, a blocked worker can resume after the registry is closed unless plan-operation ownership is integrated with A8’s nonquiescent containment fence.

**Impact:** the corrected boundary is fail-closed only before verifier resolution. Close can claim admission records closed while admitted work remains live, and generation publication can race past an operation that has already shed its admission proof. This creates a stale-generation execution/delivery path and a false-quiescence boundary under the text’s own ordering. It is a protocol/lifecycle architecture defect, not a demand for future database or concurrency proof.

**Required correction:** because two architectural remediation rounds are already consumed, this report does not authorize a third patch. Operator-directed redesign must make admission resolution lifetime-bound. A sufficient architecture would require the verifier to issue an unforgeable operation lease/guard, not return an unconstrained raw plan:

- lease acquisition atomically validates handle, runtime, epoch, binding, generation, and record state;
- the backend may access the private plan only through that live lease;
- lease release occurs only after lowering, adapter work, fetching/assembly, and snapshot or delivery publication complete or enter typed containment;
- close transitions to draining, blocks new leases, and reaches `CLOSED` only after all leases quiesce; timeout returns the accepted nonquiescent/unresolved outcome;
- migration blocks new old-generation leases and cannot publish the new generation until existing old-generation leases drain or the migration refuses before effect;
- cancellation or a non-killable worker retains the lease/containment until authoritative quiescence;
- backend entry and every independently effectful continuation reject a released, stale, cross-runtime, or cross-generation lease.

Equivalent fencing is acceptable only if it establishes the same whole-operation ownership and quiescence properties without exposing a reusable raw plan.

**Closure/regression test:** under a genuine context, insert barriers immediately after verifier resolution and before lowering, adapter invocation, first fetch, snapshot watermark capture, and result/delivery publication. At each barrier, race runtime close, force-close timeout, generation migration, reopen, and registry-epoch change. Verify:

1. no old-generation adapter invocation begins after revocation;
2. migration cannot publish the new generation while an old-generation admitted operation may still use its plan;
3. close cannot report `CLOSED` while any resolved plan operation remains live;
4. timeout/non-killable paths return typed nonquiescent containment and retain ownership;
5. stale operations cannot publish rows, snapshots, totals, refreshes, or deliveries after revocation;
6. exact current leases succeed, while copied/released/cross-runtime/cross-generation leases refuse;
7. static architecture checks fail if a verifier can return or cache a raw plan beyond the lifetime guard.

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Raw-plan and mixed-version bypass:** execute, snapshot, subscribe, and refresh are handle-only; there is no bare-plan overload or public unwrap. Old bare-plan entries refuse, and `plan_admission_v1` is required at open.
- **Forged semantic provenance:** rebuild-and-compare still covers the complete envelope, recursive closure, authority requirements, functions, result meaning, origin, and binding identity. Correctly digested same-origin semantic mutants refuse.
- **Handle forgery/substitution:** handles are exact-instance, noncopyable, nonserializable, and registry-local. Structural copies, fabricated lookalikes, extracted plans, other-runtime handles, closed-runtime handles, and pre-reopen handles cannot resolve.
- **W1 amendment honesty:** structural result roles and admitted-handle/verifier protocol changes remain explicit separately reviewed prerequisites. Current W1 bytes are not presented as already amended.
- **Hostile roots:** fixed payload, string, name, nesting, DAG, expression, result, subplan, parameter, work, and depth limits have deterministic preparse/refusal ordering. Dominated limits no longer require impossible isolated witnesses.
- **Authority and disclosure:** canonical roots contain requirements, not grants, and exclude trusted context, principal, writer, effective scope, secrets, parameter values, and physical defaults.
- **Result integrity:** structural aliases remain distinct from visible output; missing/unexpected columns, duplicate keys, orphan children, optional over-cardinality, and decode faults refuse instead of silently overwriting.
- **SQL hostility and physical provenance:** logical names resolve only through authored mappings; identifiers are quoted and values are bound. No schema-name dispatch or guessed physical name is admitted.
- **Query/question separation:** query-only expression capability remains available to queries; only questions derive footprints and live routing from the admitted plan closure.
- **Scope control:** external capture, provider integration, PostgreSQL execution, crash/restart proof, public names, W3 Surface, and P12 remain deferred without being silently revived or claimed complete.

## 3. Risks and next action

Implementation-only evidence remains appropriately deferred: real SQLite/PostgreSQL execution, driver cancellation, crash/restart, delivery, and supported-server behavior. The W1 structural-role and admitted-handle amendments remain prerequisites and are not enacted by accepting this document.

The single next action is to stop the W2 lane and request operator redesign-or-accept direction for P2-1. It is a new architectural root discovered after the second architecture remediation, so the review-loop cap forbids another ordinary architecture patch on this object. Design acceptance, W1 amendment work, and W2 implementation remain blocked.
