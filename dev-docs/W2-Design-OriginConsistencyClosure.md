# W2 shared query-planning design — ORIGINATING CONSISTENCY CLOSURE REVIEW

**Review object:** corrected `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`, in nine-file `W2-Design-MANIFEST-2.sha256` at SHA-256 `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`; design draft, not accepted or implementation authority  
**Baseline:** preserved initial design SHA-256 `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`; 13 control, 48 source and 26 accepted-W1 inputs read directly from the pinned filesystem tuple under the accepted no-Git exception  
**Date:** 2026-10-03  
**Axis:** Focused originating-reviewer verification of Consistency P2-1, P2-2 and P2-3. Independent, adversarial and read-only. Current-round reports and other closure reports were neither read nor used. Filed verbatim by the lane owner.

**Verdict: GO** — all three original Consistency P2 findings are closed on the corrected design; no new finding or new architectural root cause was found. This verdict closes the originating Consistency counterexamples only. It does not accept the design, authorize implementation, or waive the explicitly required W1 result-shape amendment.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected design | Status |
|---|---|---|---|
| P2-1 | Define hidden structural keys and five result vectors; use current W1 only if adequate, otherwise declare a reviewed amendment prerequisite | Verified at `W2-QueryPlanningDesign.md:203-251`, `:550-555`, `:586-592`, `:614-615`, `:646-650`. The design now states exact hidden aliases, types and assembly behavior, supplies all five required vectors, acknowledges that current W1 `ResultField` cannot encode visibility/structural role, requires a reviewed W1 amendment, and mandates refusal rather than a false projection before that amendment | **CLOSED** |
| P2-2 | Close every canonical leaf/value schema and registry; choose one path model; provide reachable-schema and semantic/source-detachment tests | Verified at `W2-QueryPlanningDesign.md:71-108`, `:328-353`, `:529-537`, `:548-555`. `Order`, `TieBreak`, defaults, authority requirements, subplans and functions now have exact schemas; decoded plans use only inherited `I.PathRef`; source text/locations are excluded canonically; six registries and recursive annotation closure cover all reachable forms | **CLOSED** |
| P2-3 | Define deterministic backend-neutral function fingerprints, exact `same` semantics, dialect separation, golden vectors and mutations | Verified at `W2-QueryPlanningDesign.md:110-145`, `:573-575`. The per-function algorithm is explicit, excludes SQL, defines the inherited `same` projection, separates dialect implementation versions, provides all nine pure-entry fingerprints and names semantic mutation vectors. An independent in-memory reproduction matched all nine hashes exactly | **CLOSED** |

## Changed-range analysis

The initial document is preserved byte-for-byte as `W2-QueryPlanningDesign-Initial.md` at its original SHA. The corrected range is one consolidated design amendment implementing the remediation plan.

For the original Consistency roots:

- Section 3.1 replaces the unused `PlanPath`/underspecified metadata scheme with one decoded path model and a complete inline-value registry.
- Section 3.3 replaces the false “lossless” current-W1 projection claim with exact structural aliases, five normative vectors and an explicit W1 amendment/refusal gate.
- Section 5 adds recursive schema-closure requirements.
- Sections 9–11 add executable future gates and explicit ownership prerequisites matching those decisions.
- Function semantics now have a deterministic backend-neutral fingerprint contract and independently versioned dialect implementations.

The amendment also adds provenance admission and resource-profile architecture for the other axis’s remediations and corrects distinct ordering to match inherited SQLite behavior. I inspected those changes only for contradiction with the three Consistency closures. They do not reopen them.

This is remediation 1. The merged plan classifies one other-axis root as architectural; none of the three originating Consistency roots was architectural, and this focused verification found no new architectural root.

## 0. Evidence base

At both review boundaries:

- `W2-Design-MANIFEST-2.sha256` hashed to `4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521`.
- The corrected design hashed to `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`.
- The preserved initial design hashed to `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`.
- `W2-Design-RemPlan.md` and `W2-Design-DRAFT-2.md` hashed to `53646ff9…` and `e85d885d…`.
- `shasum -a 256 -c` passed for the nine-file corrected design manifest and recursively for all 48 source, 13 control and 26 W1 entries.
- Inventory counts remained exactly 9/48/13/26.

I read the remediation plan, corrected testimony, complete corrected design and a unified comparison with the preserved initial design. I retraced the original counterexamples against:

- current W1 `ResultField`/`ResultShape` at `src/garns/backends/contracts/semantic.py:62-102`;
- inherited hidden key selection and visible-row assembly at `src/garns/lower_sqlite.py:543-599` and `src/garns/engine.py:287-303`;
- inherited path/expression forms at `src/garns/ir.py:177-390`;
- inherited function registry and `same` behavior at `src/garns/calls.py:16-57`;
- accepted A2’s opaque-root, type and named nested-owner requirements.

A permitted in-memory Python 3.14 probe reconstructed the specified compact JSON and SHA-256 fingerprint for every pure `calls.REGISTRY` entry. All nine values matched the corrected design:

- `text.normalize`: `1eba5a13…`
- `text.lower`: `d80efcd9…`
- `text.upper`: `0bd65131…`
- `text.length`: `f846ff93…`
- `text.concat`: `4f90932c…`
- `math.abs`: `7621d62d…`
- `math.round`: `8e452da3…`
- `money.round`: `4b30ba60…`
- `money.cents`: `e548dbfd…`

No files, services, databases or Git state were modified; no build or implementation gate was run.

## 2. Invariant analysis

### P2-1 counterexample

The original ordinary-query counterexample had a hidden subject identity key but only a visible `customer` field. The corrected design gives that identity the structural alias `$key.identity`, subject identity type and structural-key role, excludes it from the user row, and retains it in the key tuple. Optional/windowed and grouped hidden-key variants receive equivalent exact treatment. Distinct results use visible fields directly, and nested parent/child keys are specified separately.

Crucially, the correction does not claim those roles already exist in W1. Lines 223-236 state that current W1 is insufficient; lines 248-251 require affected projection to refuse until an independently reviewed W1 amendment exists. Sections 10–12 repeat that dependency. The original false-composition defect is therefore closed by an honest prerequisite, not by silently changing accepted W1 meaning.

### P2-2 counterexample

The corrected design now permits construction of a unique schema:

- `Order` and `TieBreak` are closed and field-complete.
- `ParameterDefault`, `AuthorityRequirement`, `Subplan` and `FunctionUse` have exact multiplicity, ordering and validation rules.
- Only inherited `I.PathRef` exists in decoded plans; no unused competing `PlanPath` remains.
- Source spelling and `Loc` are excluded from canonical meaning and reconstructed only as fixed neutral values.
- Six named registries plus recursive annotation closure cover every reachable canonical form.
- Only relational nodes are content-addressed; other forms are explicitly inline.
- Golden vectors distinguish semantic changes from source spelling/location changes.

The original inability to define one codec, validator and exhaustive consumer set is removed.

### P2-3 counterexample

The corrected fingerprint is derived only from qid, pure status, ordered parameter classes, exact result rule and a versioned semantic schema. It does not hash the SQLite SQL template. The inherited `same` behavior is stated as argument-zero scalar base/class with optional/list dimensions stripped, matching `calls.result_type()`.

Dialect SQL changes advance an independent dialect implementation version and invalidate dialect SQL caches without changing plan bytes. Semantic changes alter the per-function fingerprint; semantic-schema changes require a new plan format. The independently reproduced golden values confirm that the stated algorithm is deterministic over the current registry.

## 3. Risks and next action

The corrected design intentionally remains non-executable for ordinary, grouped and nested W1 plans under the current accepted W1 bytes. That is now a declared prerequisite rather than an unresolved design contradiction.

The next action implied by this closure is to complete the fresh full design reviews. If the design is accepted, the manager must separately scope and independently review the W1 result-shape amendment before launching implementation, then issue an execution brief assigning runtime admission and legacy integration ownership.
