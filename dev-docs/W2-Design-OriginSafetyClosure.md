# W2 shared query-planning design — ORIGINATING SAFETY CLOSURE REVIEW

**Review object:** corrected `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`, under nine-file `W2-Design-MANIFEST-2.sha256` at SHA-256 `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`  
**Baseline:** initial design preserved as `W2-QueryPlanningDesign-Initial.md` at SHA-256 `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`; recursively pinned 48-file source, 13-file control, and 26-file accepted W1 tuples were read directly from the filesystem and verified at both boundaries  
**Date:** 2026-10-03  
**Axis:** Focused originating-reviewer Safety closure of P2-1 and P2-2 only. Independent, adversarial, read-only. Current-round reports and other closure reports were neither read nor used. Filed verbatim by the lane owner.

**Verdict: GO** — both original Safety P2 findings are closed at the design level. No new root cause was found during focused retracing. This report does not accept the design, substitute for the fresh full reviews, authorize implementation, or claim future executable evidence.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected design | Status |
|---|---|---|---|
| Safety P2-1 | Deterministic runtime-owned rebuild-and-compare admission binds the complete plan/envelope and recursive closure to read identity and origin; caller-constructed plans cannot execute | Re-traced the original correctly digested same-origin mutation and relabeling sequences against §§5.3, 6, 8, 10 and 11 | **CLOSED** |
| Safety P2-2 | Mandatory `garns.plan-limits/1` fixes resource ceilings, counting, parser bounds, precedence, interoperability and boundary vectors | Re-traced broad, deep, shared-DAG, combined-work, malformed UTF-8, duplicate-key, unknown-profile and mixed-reader cases against §§5.2 and 10 | **CLOSED** |

## Changed-range analysis

The corrected design materially changes the shared plan architecture, so this is architecture remediation 1 for the W2 design object.

For the originating Safety findings, the relevant additions are:

- A mandatory versioned resource profile and streaming preparse at corrected lines 357–395.
- Trusted semantic provenance through deterministic rebuild-and-compare at lines 397–428.
- Validation ordering placing binding validation and provenance admission before backend capability validation and lowering at lines 430–445.
- Full provenance-key caching at lines 513–523.
- Exact hostile-root and provenance verification obligations at lines 576–585.
- Explicit runtime ownership and legacy integration prerequisites at lines 604–621.
- A final nonclaim that the corrected design is not implementation-ready until separately reviewed ownership amendments and execution authority exist at lines 646–650.

The same consolidated correction also closes schemas, function fingerprints and result-shape conventions raised outside this focused mandate. I inspected those changes only where they affect the two original Safety counterexamples. I found no new Safety root introduced by the remediation.

---

## 0. Evidence base

Read in full or compared directly:

- `dev-docs/W2-Design-RemPlan.md`, SHA-256 `53646ff9e5258c6e1e9d60cc094bd756bb13441afca21e5f7322d6ee957fab23`.
- `dev-docs/W2-Design-DRAFT-2.md`, SHA-256 `e85d885db3dfe61c11215332b0ed69ab36d0e50b52c676dd02a37451c306b0a9`.
- Corrected `dev-docs/W2-QueryPlanningDesign.md`, SHA-256 `db8a802f…67074`.
- Preserved `dev-docs/W2-QueryPlanningDesign-Initial.md`, SHA-256 `a7d6b1dc…7dd18`.
- A unified textual comparison of the initial and corrected designs.
- Relevant accepted W1 contracts and inherited runtime evidence retained in the unchanged recursive manifests, particularly the direct constructibility of `Plan`/`FrozenPlanRoot`, `BindingIdentity.validate_plan`, the existing resolved-read lookup, scope/capability binding, plan caching, and live refresh paths.

At START and END:

- `W2-Design-MANIFEST-2.sha256` had the required SHA-256
  `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`.
- All nine manifest entries verified.
- `W2-DesignSourceInputs.sha256` verified 48/48.
- `W2-DesignControlInputs.sha256` verified 13/13.
- `W1-RegistryContainmentRedesign-MANIFEST-3.sha256` verified 26/26.
- The corrected, initial, remediation and draft hashes remained unchanged.
- No files, builds, databases, services, dependencies or Git/GWZ state were modified.

No future implementation test was demanded or treated as having run.

## 1. Findings

No open finding remains from the originating Safety review.

## 2. Invariant analysis

### Safety P2-1 — closed

The original defect was that canonical encoding and a matching digest established byte integrity but not that the root represented the named resolved read. A same-origin attacker could construct a valid root, remove scope or another narrowing operation, recompute its digest, retain a matching outer envelope and binding origin, and potentially reach lowering.

The corrected design now closes each part of that sequence:

- It explicitly states that canonical integrity is not provenance (`:397-400`).
- The trusted runtime retains the exact resolved `Program` and authored `WorldIR` for the opened binding (`:400-403`).
- Before capability validation or lowering, it deterministically rebuilds the complete expected W1 envelope for the candidate `read_qid` (`:403-407`).
- Comparison covers canonical payload, digest, outer W1 values and `PlanOrigin`, including noun, parameters/defaults, result, live bound, authority requirements, function fingerprints, root DAG and every recursively reachable subplan (`:403-407`).
- Admission ownership is explicit: the pure bridge rebuilds but grants no trust; the runtime owns admission and caching; the backend owns neither (`:409-415`).
- `AdmittedPlan` is process-local, opaque, nonserializable and not publicly constructible (`:409-413`).
- The cache key includes read, world, IR digest, storage digest, generation, format, profile, full function-fingerprint set and canonical digest, with explicit eviction triggers (`:416-420`).
- Recursive subplans compare as a closure rather than by qualified name alone, and relabeling refuses (`:419-420`).
- Until the runtime integration exists, serialized or caller-constructed `Plan` values are prohibited from execution (`:422-424`).
- The exact original mutations—scope, authority, archive, member, identity, predicate, result and subplan—are required to refuse with `PLAN_PROVENANCE_MISMATCH` before lowering or adapter invocation (`:424-428`, `:582-585`).
- The validation pipeline places trusted admission after binding-origin validation and before static capability validation, authority evaluation, lowering and execution (`:430-445`).
- Runtime integration and affected legacy paths require a separately reviewed ownership amendment; the design does not silently authorize them (`:604-621`).

Replaying the original counterexample therefore reaches exact rebuild comparison and differs from the trusted root before lowering. Keeping the same origin and recomputing a digest does not help; omitting an authority requirement or scope decorator changes the compared payload. Relabeling another legitimate plan fails outer and closure equality. Exact trusted bridge output remains the specified success case.

The architectural correction is concrete and implementable without pretending the current source already enforces it. P2-1 is closed at the design gate.

### Safety P2-2 — closed

The original defect was the promise of hostile-root “limits” without values, counting rules, parser protection, diagnostic precedence or an interoperability policy.

The corrected `garns.plan-limits/1` profile now supplies:

- A mandatory profile fixed to `garns.plan/1`, with no silent per-process variation (`:357-360`).
- Inclusive limits for payload bytes, JSON nesting, individual and total strings, qualified identifiers, unique relational nodes, edge occurrences, expression occurrences/depth, subplans/depth, result items/nesting, functions, parameters/defaults, combined semantic depth and total validation work (`:362-377`).
- Shared-DAG rules: unique nodes count once for node capacity, while every reference and comparison consumes edge/work budget (`:368-370`, `:388-389`).
- A byte-counting streaming preparse that bounds bytes, UTF-8, nesting, strings, tokens and duplicate-key tracking before materializing the JSON object (`:379-381`).
- Deterministic refusal precedence among payload overflow, malformed encoding/duplicate keys, profile counters, canonical/digest failures, schema/semantic failures and provenance failures (`:381-387`).
- Explicit-stack validation rather than reliance on Python recursion (`:388-389`).
- Exact-limit acceptance and limit-plus-one refusal vectors for every dimension, plus broad/shallow, deep/narrow, combined-depth/work, shared-node fan-out, malformed UTF-8, duplicate keys, payload overflow and unknown profiles (`:391-395`).
- A compatibility rule requiring every reader claiming format/profile 1 to make the same admission decision (`:395`).
- Ordered implementation obligations repeating all exact/plus-one, combined, shared-DAG and mixed-profile attacks (`:576-581`).

The original breadth, recursion, fan-out and mixed-version sequences now have deterministic ceilings and refusal stages. The profile also defines enough counting detail to build falsifiable boundary tests without demanding that those tests already exist at this design-only gate. P2-2 is closed.

### Preserved safety boundaries

The correction does not broaden authority or implementation scope:

- The compiler bridge still issues no authority.
- Runtime trusted-context checks remain distinct from semantic plan admission.
- The root still contains requirements rather than granted authority.
- Caller parameter values and secrets remain outside canonical plan bytes.
- No current W1, runtime, backend, live, legacy lowerer or generator write is silently authorized.
- PostgreSQL execution, async behavior, concurrency, restart and delivery evidence remain future gates.
- The design expressly states that it is not fully implementation-ready under current W1 bytes and identifies the required reviewed prerequisites.

## 3. Risks and next action

Implementation can still be wrong despite a closed design: the streaming preparse, deterministic rebuild, opaque admission wrapper, cache eviction and refusal ordering require executable verification during authorized implementation. That is ordinary future implementation risk, not an open design defect.

The single next action for these originating findings is to record Safety P2-1 and P2-2 as independently closed on the corrected tuple. Overall W2 design disposition remains with the fresh peer-blind full reviewers and lane owner; this focused report neither accepts the design nor launches implementation.
