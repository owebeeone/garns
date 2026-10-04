# W2 shared query-planning design — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`; corrected design draft, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, recursively pinned by `dev-docs/W2-Design-MANIFEST-2.sha256` at SHA-256 `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`. Sources and controls were read directly from the manifested filesystem tuple under the accepted no-Git exception; no Git snapshot or cleanliness claim was used.  
**Date:** 2026-10-03  
**Axis:** Safety — degraded and bypass paths, authority and provenance preservation, hostile-input bounds, stuck states, irreversible behavior, disclosure, compatibility, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new architectural P2 finding blocks. Both original Safety findings are closed by the corrected text. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST-2.sha256` returned exactly `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`.
- The manifest contained exactly nine entries.
- `shasum -a 256 -c` passed for all nine top-level entries, including:
  - corrected design `db8a802f…08467074`;
  - corrected testimony `e85d885d…306b0a9`;
  - execution brief `5320926a…ad8327d3`;
  - remediation plan `53646ff9…57fab23`;
  - preserved initial design `a7d6b1dc…7dd18`;
  - both initial review reports.
- Recursive verification passed for all 48 entries in `W2-DesignSourceInputs.sha256`, all 13 entries in `W2-DesignControlInputs.sha256`, and all 26 entries in `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`.
- Inventory counts remained exactly 48, 13, and 26. No tuple movement occurred.

I read:

- workspace and product instructions: `AGENTS_GWZ.md`, `garns-v9-6/AGENTS.md`;
- `CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- `W2-DesignExecutionBrief.md`;
- the corrected 650-line `W2-QueryPlanningDesign.md`;
- preserved `W2-QueryPlanningDesign-Initial.md`;
- `W2-Design-DRAFT.md`, `W2-Design-DRAFT-2.md`, and `W2-Design-RemPlan.md`;
- both legitimate initial reports, including the complete initial Safety report;
- every artifact named by `W2-DesignControlInputs.sha256`, including the accepted plan, provider-neutral amendment and acceptance, governed-write amendment and acceptance, operator decisions, W0/W1 acceptance, complete W1 manifest, and frozen product layout;
- accepted A1–A15 and the complete W1 contract tuple;
- relevant manifested compiler, IR, type, function-registry, storage, lowering, engine, live, footprint, generation, and test sources.

The focused safety trace covered:

- canonical schema and outer-plan checks: corrected design lines 282–355;
- concrete resource profile and refusal precedence: lines 357–395;
- trusted rebuild-and-compare provenance: lines 397–428;
- validation, authority, capability, and lowering order: lines 430–462;
- lowering and result assembly: lines 464–500;
- admitted-plan caching and live reuse: lines 502–527;
- future implementation obligations and ownership gaps: lines 546–621;
- accepted W1 plan construction and binding checks: `semantic.py:105-175`;
- the unchanged W1 backend protocol boundary: `protocols.py:30-75`;
- A2’s requirement that capability, authority, and binding validation precede lowering and every effect: `docs/adr/A2-backend-contract.md:8-16`;
- initial-to-corrected textual diff for all remediation changes.

No file, Git state, database, service, dependency, or process state was modified. No build or implementation test was run.

### Prior-finding closure

| Prior finding | Classification | Corrected evidence | Verdict |
|---|---|---|---|
| Consistency P2-1 — hidden structural keys cannot project losslessly to accepted W1 `ResultShape` | bounded | Lines 213–251 define reserved structural aliases, visible-versus-structural assembly, five normative vectors, and explicit refusal of affected W1 projection until a separately reviewed W1 role/visibility amendment exists. | Closed for design coherence. The amendment is correctly a prerequisite, not silently assumed authority. |
| Consistency P2-2 — canonical value algebra is incomplete | bounded | Lines 73–108 define one path model and the inline forms; lines 329–355 define six exact registries and reachable-schema closure. | Closed. |
| Consistency P2-3 — function semantic revision has no derivation | bounded | Lines 110–145 define the backend-neutral fingerprint input, current goldens, semantic-change behavior, and independent dialect implementation versioning. | Closed. |
| Safety P2-1 — canonical integrity is mistaken for trusted provenance | architectural | Lines 397–428 select deterministic rebuild-and-compare over the complete envelope and recursive closure; same-origin semantic mutants and relabeling must refuse before lowering. | Original counterexample closed, subject to the new boundary defect below. |
| Safety P2-2 — hostile-root limits have no concrete contract | bounded | Lines 357–395 define the mandatory profile, inclusive limits, counting rules, streaming preparse, refusal precedence, iterative validation, shared-DAG accounting, exact-boundary and mixed-version vectors. | Closed. |

### Changed-range analysis

The material correction adds four relevant safety structures:

1. a closed canonical schema and function fingerprint contract;
2. an explicit refusal boundary for W1 result shapes that cannot yet represent structural fields;
3. a fixed `garns.plan-limits/1` hostile-input profile;
4. trusted runtime rebuild-and-compare producing an opaque `AdmittedPlan`.

The first three close their cited counterexamples without widening present write authority. The fourth closes semantic equivalence at the runtime admission point, but then discards its proof before crossing the existing backend protocol seam. That changed boundary is the sole new blocker.

## 1. Findings

### [P2-1] Admission proof is discarded before the backend execution seam

**Classification:** architectural.

**Location:** `W2-QueryPlanningDesign.md:409-415`, especially the rule that runtime unwraps an `AdmittedPlan` back to its exact ordinary W1 `Plan` and passes that to the unchanged Plan-consuming backend protocol; pipeline at `:432-445`; cache/use statements at `:513-519`; ownership table at `:610-615`. The accepted protocol still exposes bare-plan execution at `src/garns/backends/contracts/protocols.py:35-39,74-75`.

**Violated invariant:** only a plan proven byte-for-byte equivalent to trusted compilation may reach lowering or adapter execution. The design also inherits A2’s requirement that validation precede lowering and every effect. A successful check at one caller does not enforce that invariant if the callee’s executable interface remains indistinguishable from the pre-admission bare-plan interface.

**Reproduction/state sequence:**

1. Construct a canonical, correctly digested same-origin `Plan` that removes `ScopeFilter`, `AuthorityRequirement`, archive/member/identity narrowing, a predicate, result expression, or recursive subplan. This is the original forged-root counterexample.
2. The intended runtime path would call `admit_plan` and reject it.
3. A legacy, mixed-version, alternate internal, subscription, snapshot, or direct connection call instead invokes the accepted W1 seam:
   - `AsyncConnection.execute(plan, ...)`;
   - `AsyncConnection.consistent_snapshot(plan, ...)`; or
   - `AsyncBackend.subscribe(plan, ...)`.
4. Those methods receive the same directly constructible `Plan` type as before. The proposed `AdmittedPlan` is unwrapped before this seam, is not part of the protocol, and carries no backend-verifiable marker.
5. The backend therefore cannot distinguish a plan that passed rebuild-and-compare from one that bypassed it. The design says callers “must not execute” unadmitted plans, but supplies no type, token, registry check, or mandatory backend re-admission that makes bypass impossible or detectably refusing.
6. In a partial migration or stale call path, the forged root can consequently reach lowering despite the new provenance algorithm. This does not require malicious code inside the trusted process; an incompletely rewired legacy path is sufficient.

The proposed cache does not repair this boundary. It is runtime-owned and keyed by candidate metadata, but the bare `Plan` passed to the backend neither proves a cache hit nor requires the backend to consult that cache.

**Impact:** the original scope/provenance vulnerability remains reachable through exactly the degraded and mixed-version paths this axis must attack. The design’s strongest safety claim depends on every caller voluntarily using a new runtime helper while retaining executable interfaces that accept unproven values. A missed integration path can widen results or alter named-read meaning without any refusal at the backend boundary.

**Required correction:** preserve or independently verify provenance across every executable seam. The design must choose one enforceable shape, for example:

- amend the W1/backend protocol so execution, snapshot, and subscription accept an opaque runtime-issued admitted-plan capability rather than a bare `Plan`; or
- require each backend entry point to validate a process-local admission record/token bound to the exact plan digest, binding identity, runtime generation, function set, and recursive closure before lowering; or
- perform deterministic rebuild-and-compare again at every backend entry that accepts a bare plan.

If a protocol amendment is required, name it as a launch prerequisite alongside the result-shape amendment. Merely assigning legacy wiring ownership is insufficient: the type/call boundary must make bypass refuse. Define the migration ordering so no old bare-plan route remains executable while new admission is assumed.

**Closure test:** exercise every plan-consuming protocol entry through both intended and bypass paths:

1. exact bridge-produced admitted plan succeeds for execute, consistent snapshot, and subscribe;
2. the same canonical same-origin semantic mutants used for original Safety P2-1 refuse at each backend entry even when admission is deliberately skipped;
3. a raw `Plan` extracted from or byte-equal to an admitted plan cannot be used as an admission substitute;
4. an admitted object/token from another runtime, binding, generation, read, storage digest, or closed/reopened runtime refuses;
5. mixed-version wiring with one retained legacy bare-plan caller fails closed before SQL construction or adapter invocation;
6. static checks enumerate every `Plan` consumer and fail if a new executable bare-plan entry is introduced.

## 2. Invariant analysis

The following adversarial attacks did not expose additional findings:

- **Original semantic-provenance mutants:** deterministic rebuild-and-compare covers the full outer envelope, canonical root, authority requirements, function fingerprints, recursive subplans, origin, and binding identity. Same-origin semantic mutation and relabeling are explicitly required to refuse.
- **Amendment prerequisites:** the proposed W1 result-shape amendment is not treated as already accepted. Affected plan construction refuses until the contract can represent structural roles, preserving coherence without authorizing W1 writes.
- **Hostile resource inputs:** the fixed profile closes deployment-local variation and gives deterministic bounds for payload, strings, identifiers, JSON nesting, DAG nodes and edges, expressions, subplans, results, functions, parameters, combined depth, and total validation work. Streaming preprocessing and explicit stacks avoid relying on Python recursion for rejection.
- **Malformed encoding:** payload overflow, malformed UTF-8/JSON, duplicate keys, noncanonical bytes, digest mismatch, unknown profile/tags/fields, cycles, orphans, and sidecar mismatch have explicit refusal stages before dialect or adapter work.
- **Authority disclosure and confused-deputy state:** the root contains requirements only, not granted scope, context, principal, writer, secrets, or parameter values. Runtime authority remains separately checked after provenance.
- **Cache staleness:** the proposed runtime cache key includes read, world, IR/storage digests, generation, format/profile, function fingerprints, and canonical digest; reopen, migration, function change, or runtime close evicts it. No defect was found within that cache rule itself.
- **Physical-name and SQL injection paths:** logical names resolve only through authored mappings; physical identifiers are quoted; caller, default, scope, clock, parent, and literal values are bound rather than interpolated.
- **Unsupported capability behavior:** static capability refusal precedes SQL construction, while backend/version/namespace refusal precedes adapter invocation or effect.
- **Result corruption:** hidden structural aliases are separated from visible output, and assembly refuses missing/unexpected columns, duplicate keys, unattached children, optional over-cardinality, and type decode faults rather than overwriting.
- **Query/question leakage:** only questions derive footprints; query-only expressive behavior does not inherit live restrictions. The same admitted plan is intended for question initialization and refresh.
- **Scope creep:** the document identifies all out-of-W2 legacy, runtime, W1, and live integration paths as separately reviewed prerequisites. It does not authorize those writes, revive external capture, claim PostgreSQL/async/restart proof, or absorb the W1 P3 assigned to W3.

## 3. Risks and next action

Residual implementation risks below the finding bar remain appropriately deferred: real SQLite/PostgreSQL execution, async cancellation, crash/restart, concurrency, live delivery, server-version behavior, and public Surface evidence. Canonical JSON and the chosen resource maxima still require implementation proof, but their design contracts are falsifiable.

The single next action is one final architectural design correction that carries enforceable admission status across every execute/snapshot/subscribe backend boundary and states the required protocol/ownership amendment and migration ordering. This is a new architectural root after remediation 1, so it consumes the object’s one remaining architectural remediation allowance. The revised tuple requires fresh full Safety review plus focused re-execution of this bypass sequence; the original reviewer should separately verify the two original counterexamples remain closed.
