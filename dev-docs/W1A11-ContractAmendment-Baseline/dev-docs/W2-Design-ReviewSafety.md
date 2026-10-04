# W2 shared query-planning design — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`, design draft, not accepted or implementation authority  
**Baseline:** recursively manifested read-only source/control/W1 tuples under `/Volumes/projects/limbo/datascad/garns-v9-6`; no Git snapshot was used. Review manifest SHA-256 `4014506528289e2d7d31c45ca433960271c8e5c3dd0e8486a7f53a183a425881`; 48-file source manifest, 13-file control manifest, and 26-file accepted W1 manifest verified at both review boundaries.  
**Date:** 2026-10-03  
**Axis:** Safety — malformed and forged plans, authority preservation, bounded hostile-input handling, result integrity, degraded paths, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block: one architectural provenance/authority root and one bounded resource-policy root. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## 0. Evidence base

The review read and checked:

- Workspace and product instructions: `AGENTS_GWZ.md`, `garns-v9-6/AGENTS.md`.
- Full review-loop process and canonical prompt template:
  `/Users/owebeeone/.claude/skills/review-loop/SKILL.md` and
  `references/review-prompt-template.md`.
- Current program state and complete W2 testimony:
  `dev-docs/CurrentProgramCheckpoint.md`,
  `dev-docs/W2-DesignExecutionBrief.md`,
  `dev-docs/W2-QueryPlanningDesign.md` lines 1–459, and
  `dev-docs/W2-Design-DRAFT.md`.
- The complete control tuple, including the accepted implementation plan,
  provider-neutral seam and acceptance, governed-write amendment and acceptance,
  operator decisions, W0/W1 acceptance, A1–A15, and frozen
  `docs/PRODUCT_LAYOUT.md`.
- The accepted W1 semantic boundary, particularly
  `src/garns/backends/contracts/semantic.py:11-175`,
  `protocols.py`, `authority.py`, `values.py`, and their contract tests.
- Relevant inherited semantics and consumers:
  `ir.py:177-490`, `types.py:30-83`, `calls.py`,
  `resolve_read.py:530-789`, `storage.py:63-302`,
  `lower_sqlite.py:28-70,383-599`, `engine.py:183-355`,
  `footprint.py:45-223`, `live.py:95-254`, and the pinned inherited tests,
  especially resolve, static/dynamic, live, metamorphic, generation and
  contract coverage.
- Source searches covered scope/unscoped handling, optional-single behavior,
  grouping, rank, total, nesting, plan caches, lowering, parameter validation,
  footprints, and live refresh/fold behavior.

At both START and END:

- `shasum -a 256 dev-docs/W2-Design-MANIFEST.sha256` returned
  `4014506528289e2d7d31c45ca433960271c8e5c3dd0e8486a7f53a183a425881`.
- The design, brief and draft hashes were respectively
  `a7d6b1dc…7dd18`, `5320926a…327d3`, and `54659f6f…f884`.
- `shasum -a 256 -c` passed for:
  - `W2-Design-MANIFEST.sha256`;
  - `W2-DesignSourceInputs.sha256` — 48/48;
  - `W2-DesignControlInputs.sha256` — 13/13;
  - `W1-RegistryContainmentRedesign-MANIFEST-3.sha256` — 26/26.
- No files, services, databases, dependencies, or Git state were modified.
  No build or future implementation gate was run.

## 1. Findings

### [P2-1] Canonical integrity is mistaken for trusted plan provenance

**Classification:** architectural.

**Location:** `W2-QueryPlanningDesign.md:210-255`, especially the canonical-root construction and validation sequence at lines 236–246; authority rules at lines 231–234 and 257–288; plan consumption and caching at lines 340–345. The accepted execution protocol consumes a caller-supplied W1 `Plan` at `src/garns/backends/contracts/protocols.py`, while `FrozenPlanRoot` and `Plan` are directly constructible immutable values at `semantic.py:123-160`.

**Violated invariant:** a named read must execute the semantics resolved from the accepted qualified IR, and caller-controlled data must not widen scope or replace runtime-owned authority. Digest verification proves only that payload bytes match a supplied digest; it does not prove those bytes were produced by the trusted bridge for `Plan.read_qid`.

**Reproduction/state sequence:**

1. Obtain the accepted world, storage and generation values, which are binding identity rather than secret authority.
2. Construct a canonical, structurally valid plan for an existing scoped read.
3. Keep the legitimate outer `read_qid`, noun, parameters and a self-consistent result shape, but omit the read’s `ScopeFilter`, predicate, `ExcludeArchived`, `MemberOf`, or other narrowing semantics. In the scope attack, also omit `authority_requirements`.
4. Canonically encode the altered DAG and compute its correct SHA-256 digest.
5. Attach the genuine binding-origin tuple.
6. The specified validation sequence checks format, limits, canonical encoding, digest integrity, tags, DAG structure, types/functions/result shape, selected outer `Plan` fields and binding identity. It never compares the full root to a trusted compilation of the resolved `Read`, nor requires a runtime-issued plan identity or allow-listed `(read_qid, origin, digest)` record.
7. The altered root can therefore reach lowering with no `ScopeFilter` and no unscoped capability requirement. Runtime validation has no claimed scope to reject and may return rows across scopes. The same mechanism can silently remove archival, identity, membership or user predicates while retaining the legitimate named-read envelope.

The design’s hostile-root tests at lines 397–401 cover malformed values, mismatched outer fields and forged origins, but not a well-formed, correctly digested plan whose semantics differ from the named read. `BindingIdentity.validate_plan` at `semantic.py:170-175` checks only world/IR/storage/generation, not root provenance or equivalence. The inherited runtime currently avoids this defect by retrieving the resolved `Read` and binding scope/unscoped authority from it at `engine.py:201-211,282-329`; W2 explicitly removes that second semantic input.

**Impact:** a self-consistent forged root can widen a named read’s result or change its meaning without forging origin metadata. This defeats qualified read identity, scope isolation, archive/member discrimination and the rule that public authority comes only from the trusted context. It also makes plan-cache reuse unsafe because a cache keyed as “one plan per read/binding/generation” has no specified trusted-digest admission rule.

**Required correction:** define one closed provenance rule before plan consumption. Acceptable shapes include:

- runtime consumption only of a runtime/compiler-issued plan whose exact digest is registered against `(read_qid, origin)` during trusted compilation; or
- deterministic rebuilding of the expected root from the exact resolved `Read` and authored world followed by exact digest equality before admission.

The correction must state who owns that registry/rebuild, how recursive subplans are included, when cache entries are invalidated, and that structural validity alone never authorizes execution. Scope, unscoped capability, member/archive behavior, parameters, result shape and every predicate/composition edge must be covered by the same provenance comparison rather than individually inferred after decoding.

**Closure test:** construct canonical, correctly digested same-origin mutants that independently remove or replace `ScopeFilter`, `AuthorityRequirement`, `ExcludeArchived`, `MemberOf`, `IdentityFilter`, `Filter`, a result expression and a recursive subplan. Each must refuse before lowering or adapter invocation. Replaying the exact bridge-produced root must succeed, and a trusted plan for another `read_qid`, storage digest or generation must not be relabelable by changing only its outer envelope.

### [P2-2] Hostile-root resource limits have no concrete contract

**Classification:** bounded.

**Location:** `W2-QueryPlanningDesign.md:64-69`, `:150-166`, `:212-246`, `:274-281`, `:355-371`, and hostile tests at `:397-401`.

**Violated invariant:** malformed or adversarial roots must have deterministic, bounded refusal behavior before backend work. The design promises byte-length, depth and node-count limits but supplies no limits, counting rules, defaults, aggregate budget, or refusal precedence.

**Reproduction/state sequence:**

1. Submit a canonical payload containing a shallow but extremely broad node/result/subplan/function registry, or deeply nested expressions and nested result shapes near an implementation-chosen recursion limit.
2. Alternatively use very long qualified identities, large arrays of references, or extensive shared-DAG fan-out whose serialized bytes remain below one implementation’s unspecified byte ceiling.
3. One implementation may parse, allocate and validate the root; another may refuse it based on different local limits. A recursive validator may raise an incidental recursion or memory failure instead of the promised typed malformed/resource refusal.
4. Because depth/node limits can only be evaluated after at least some decoding, the text’s stated order does not define how JSON parsing itself is bounded or how duplicate-key detection and canonical comparison avoid constructing the entire hostile object first.

This is not a demand for future performance evidence. It is a missing design decision: implementations cannot produce compatible admission/refusal behavior or falsifiable boundary tests from “limits” with no values or counting semantics.

**Impact:** roots can cause excessive CPU, memory or recursion consumption before refusal, and SQLite/PostgreSQL/runtime consumers can disagree over whether the same canonical plan is admissible. Mixed-version deployments can consequently accept a cached plan on one process and reject it on another without a generation or format change.

**Required correction:** specify versioned limits for at least payload bytes, JSON nesting, relational nodes, expression nodes, subplans, result nesting/fields, function uses, parameters/defaults, identifier/string bytes, reference fan-out and total validation work. Define whether shared DAG nodes count once or per traversal, how recursive subplan and expression depths combine, which refusal code/stage wins, and how parsing is bounded before object construction. State whether limits are fixed by `garns.plan/1` or carried by a separately versioned compatibility profile; deployment-local silent variation is unsafe.

**Closure test:** for every dimension, verify exact boundary acceptance and boundary-plus-one typed refusal before dialect/adapter invocation. Include breadth-only, depth-only and combined-budget bombs; duplicate-key and malformed UTF-8 cases; a small-byte/high-fan-out DAG; and mixed-version readers proving identical admission for the same format/profile.

## 2. Invariant analysis

The following attacks did not expose additional blocking defects:

- **Outer envelope and origin mismatch:** the design explicitly requires agreement between payload and outer read/noun/parameters/result/live-bound values, then W1 binding validation for world, IR, storage and generation (`:236-246`). Stale/future generations and mismatched storage origins refuse before dialect invocation.
- **Malformed encoding:** duplicate JSON keys, unknown fields/tags, noncanonical bytes, digest mismatch, missing nodes, cycles, orphans and diagnostic-sidecar substitution are explicitly rejected (`:212-255`, `:355-371`). The remaining issue is resource-policy closure, not absence of malformed-input intent.
- **Secret and authority disclosure:** the root excludes context, effective scope, principal, writer, secrets and parameter values. `authority_requirements` is a requirement rather than a claimed grant, and runtime context checks remain after binding (`:231-234`, `:283-288`).
- **Physical provenance and SQL hostility:** the lowerer resolves logical identities through authored `RelationMapping`; no physical name is synthesized. Identifiers are quoted and values are separately bound through generated positional slots (`:290-300`). The design does not claim current storage syntax accepts arbitrary hostile names.
- **Unsupported capability timing:** static unsupported nodes, functions and types refuse before SQL construction; dynamic backend/server/namespace capability refusal precedes adapter invocation (`:274-281`).
- **Expression and function ownership:** existing qualified `I.Operand`/`I.Expr` classes are reused, locations/source spelling are excluded from canonical meaning, and dialect functions are independently exhaustively mapped rather than copied from compiler SQL templates (`:81-100`).
- **Result cardinality and assembly:** ordinary, optional, grouped, windowed, distinct and global-aggregate keys are defined; total count is pre-window; nested association detects missing/duplicate/over-cardinality/type faults instead of overwriting silently (`:137-179`, `:302-327`).
- **Ordering/rank/window semantics:** stable tie policies are explicit for ordinary, grouped, distinct and nested rows; rank uses the same complete order; nested `last N` reverses only selection and restores ascending emission (`:302-319`).
- **Query/question separation:** only questions derive footprints; query-only expressive forms do not inherit live restrictions. Initialization and refresh are intended to consume the same plan object, with routing driven by the same recursive closure (`:329-353`).
- **Live neutrality and fold preservation:** the future verification plan covers group movement, recursive composition, bounded overflow, neutral suppression, revision-by-revision fold equivalence and zero listener scans (`:402-408`). The document correctly does not claim current runtime proof.
- **Ownership and scope:** the design names cohesive W2 paths and explicitly refuses to treat legacy engine/live/lowerer/generator integration as authorized (`:33-60`, `:420-436`). It does not silently launch W3/W4 work or claim PostgreSQL, async, restart or delivery evidence.

## 3. Risks and next action

Residual implementation risks below the finding bar remain appropriately gated: the nested-owner marker must remain consistent with accepted W1 intent; canonical JSON encoding needs one exact implementation profile; differential SQLite equality can preserve inherited bugs; and real async, PostgreSQL, concurrency, restart, authority-delivery and server semantics remain future gates rather than design evidence.

The next action is one consolidated design revision that adds trusted semantic provenance/admission for every executable root and a versioned, testable resource-limit contract. Both original counterexamples must then receive focused Safety re-verification against a newly pinned tuple.
