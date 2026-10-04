# W2 shared query-planning design — ORIGINATING SAFETY CLOSURE REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`; final design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by `dev-docs/W2-Design-MANIFEST-3.sha256` at SHA-256 `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`. Sources and controls were read directly from the manifested filesystem tuple under the accepted no-Git exception.  
**Date:** 2026-10-03  
**Axis:** Focused originating Safety closure — retrace the round-2 bare-plan bypass across execution, snapshot, subscription, refresh, and degraded or mixed-version paths. Independent, adversarial, read-only. No current fresh peer or closure report was read. Filed verbatim by the lane owner.

**Verdict: GO** — originating Safety-2 P2-1 is closed; no new P0, P1, P2, or P3 finding was identified.

---

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-3.sha256` returned exactly `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`.
- The top-level manifest contained exactly 13 entries.
- `shasum -a 256 -c dev-docs/W2-Design-MANIFEST-3.sha256` passed all 13 entries, including:
  - final design `0b8b77a0…faf7af44e`;
  - final testimony `4562fccb…029548f`;
  - final remediation plan `8141d0e5…c0be13`;
  - preserved revision-2 design `db8a802f…08467074`;
  - preserved initial design and prior-round reports.
- Recursive verification passed all 48 source entries, all 13 control entries, and all 26 accepted W1 entries.
- Counts remained exactly 13/48/13/26. No tuple movement occurred.

I read:

- workspace and product instructions;
- current program checkpoint and W2 execution brief;
- complete final design and final drafter testimony;
- complete `W2-Design-RemPlan-2.md`;
- preserved `W2-QueryPlanningDesign-Revision2.md`;
- the exact revision-2-to-final diff;
- accepted W1 `Plan`, `BindingIdentity`, and backend protocol definitions;
- relevant A2 and A12 requirements concerning pre-effect validation, generation compatibility, and stale continuation.

The focused trace covered:

- resource-profile corrections at final design lines 357–408;
- trusted semantic rebuild-and-compare at lines 410–420;
- the exact-instance handle and bound verifier seam at lines 422–448;
- provenance key and lifecycle invalidation at lines 449–457;
- snapshot, subscription, refresh, child, nested, and total consumers at lines 459–465;
- fail-closed migration ordering and mixed-version handshake at lines 467–474;
- prerequisite/non-authority statements at lines 476–482;
- ordered validation pipeline at lines 484–502;
- future bypass tests at lines 638–645;
- exact W1 amendment and ownership gap at lines 664–681.

No source, test, contract, ADR, grammar, Git, dependency, database, or service state was modified. No implementation test or build was run.

### Prior-finding closure table

| Finding | Original counterexample | Final correction | Closure |
|---|---|---|---|
| Safety-2 P2-1 — admission proof was discarded before the backend execution seam | A correctly digested forged `Plan` could bypass runtime admission by reaching `AsyncConnection.execute`, `consistent_snapshot`, or `AsyncBackend.subscribe` through a legacy, alternate, or mixed-version bare-plan path. The backend received no proof distinguishing an admitted plan from a directly constructed one. | Lines 422–448 require a reviewed W1 amendment replacing every executable bare-`Plan` parameter with an opaque, exact-instance `AdmittedPlanHandle`. Each backend object is constructed with a non-replaceable verifier bound to one runtime registry. Resolution requires registered object identity, runtime identity, epoch, OPEN state, current binding/origin/generation, and full provenance-key equality. No public unwrap, bare-plan overload, or compatibility fallback is permitted. | **Closed.** |
| Initial Safety P2-1 — canonical integrity did not establish trusted semantic provenance | Same-origin canonical mutants could remove scope, authority, archive/member/identity filters, predicates, result expressions, or recursive subplans. | The final design retains complete deterministic rebuild-and-compare at lines 410–420 and the mutant/refusal obligations at lines 476–482 and 638–645. | Remains closed. |
| Initial Safety P2-2 — hostile-root resource limits lacked a concrete contract | Resource admission and refusal behavior could vary or exhaust memory/recursion before rejection. | The fixed profile, iterative validation, streaming preparse, counting rules, and refusal precedence remain. The final correction additionally replaces impossible isolated-boundary claims with reachable, dominated, registry, payload-intersecting, and aggregate classifications at lines 357–408. | Remains closed. |

### Changed-range analysis

The final change no longer unwraps an admitted object into an ordinary plan before the backend seam. It instead:

1. makes the admitted handle part of every executable protocol signature;
2. binds backend instances to one exact registry verifier at construction;
3. makes raw plans, copied/fabricated handles, cross-runtime handles, stale epochs, closed records, and mismatched bindings unresolvable;
4. retains the same handle through initial snapshot, subscription, and refresh;
5. prevents nested, child, and total statements from becoming independent public consumers;
6. statically enumerates every route to lowering or adapter I/O;
7. requires old bare-plan routes to return `PLAN_ADMISSION_REQUIRED`;
8. requires a `plan_admission_v1` open-time handshake so mixed versions refuse;
9. delays W2 enablement until bypass enumeration and tests pass.

These are material architectural changes and correctly consume the second architecture correction. They directly close the proof-stripping mechanism rather than relying on caller convention.

## 1. Invariant analysis

The originating counterexample was retraced through each path:

- **Execute bypass:** a bare or forged `Plan` is no longer an accepted executable value. The amended backend signature accepts only a registry-issued handle, and backend lowering is reachable only after bound-verifier resolution.
- **Consistent-snapshot bypass:** snapshot uses the same handle-only seam and verifier requirements; there is no separate bare-plan compatibility route.
- **Subscription bypass:** subscription creation accepts the handle, not a plan. A handle from another runtime, registry, binding, generation, epoch, or lifecycle cannot resolve.
- **Refresh bypass:** the live instance retains and reuses the same handle rather than extracting or storing a raw plan.
- **Nested/child/total bypass:** these statements are derived inside an already verified operation and are forbidden from becoming independently executable plan consumers.
- **Extracted-plan substitution:** registry records retain the private plan, while the handle exposes no useful fields or public unwrap. Possession of byte-identical plan data does not satisfy exact object-identity lookup.
- **Fabricated or copied handle:** handles are identity-compared, noncopyable, nonserializable, and must be registered in the exact bound registry.
- **Cross-runtime or reopen reuse:** runtime identity and epoch are checked; close marks records closed before backend close, and reopen creates a new identity, registry, and epoch.
- **Binding or generation reuse:** resolution rechecks binding, origin, generation, and the full provenance key. Migration revokes the old binding set before publishing the new set.
- **Mixed-version fallback:** `plan_admission_v1` is required at open, and old bare-plan entry points refuse until removed. No migration phase permits an executable bare-plan route while relying on admitted semantics.
- **New consumer escape:** architecture checks enumerate all paths reaching lowering or adapter I/O and fail on any `Plan`-accepting entry or lowerer call without verifier resolution.

The proposed W1 protocol amendment is not enacted by this design. That is coherent rather than a defect: lines 422, 467–478, 675, and 706–711 make its independent review and acceptance a prerequisite to any W2 execution. Under current W1 bytes, W2 plans remain non-executable.

The final design also preserves the earlier proofs for canonical provenance, resource bounding, secret exclusion, authority ownership, authored physical mapping, result integrity, capability refusal, and the query/question split.

A possible verifier-resolution-versus-generation-change race does not reopen the originating bypass. Generation transition fencing and in-flight database behavior remain governed by accepted A12 and later runtime/database implementation gates; the design does not claim that handle revocation alone proves real concurrent migration safety.

## 2. Risks and next action

No further architectural or bounded design root was found. Real implementation must still demonstrate that exact-instance identity, registry epochs, lifecycle revocation, connection construction, protocol negotiation, and static consumer enumeration behave as designed; those are future implementation proofs, not missing design decisions.

The next action is manager consideration of final design acceptance. Before implementation or execution, a separately scoped and independently reviewed W1 amendment must add both structural result roles and the admitted-handle/verifier protocol, followed by an execution brief assigning runtime registry, backend, and legacy-integration ownership.
