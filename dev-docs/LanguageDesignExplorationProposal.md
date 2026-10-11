# GARNS Language Design Exploration Proposal

Status: proposed work for operator review. Approval of this proposal authorizes
design exploration, not a language choice, compiler implementation or release.

## Purpose

Explore a wider range of language designs once, using a common set of requirements
and examples, rather than repeatedly designing one feature in isolation. Produce
four materially different solutions for each active feature area, then compare
combinations as whole languages. The operator can select individual approaches or
a coherent combination after seeing their consequences.

The objective is a declarative language for data meaning, relationships, permitted
change and guarantees. Persistence, generated APIs and execution mechanisms derive
from that meaning. Pyrocat is a demanding example, not the definition of GARNS.
Maximize useful declarativity subject to semantic fidelity, predictable composition
and correctness; do not reward complexity or hidden engine behavior for its own sake.

This is a bounded exploration, not an exhaustive search or an assumption that the
current language must be replaced. Existing constructs may remain the best choice;
larger changes are legitimate candidates when they materially simplify the whole.

## Requirements and boundaries

Use [LanguageChangeRegister.md](LanguageChangeRegister.md) as the starting ledger.
Separate requirements from proposed spellings and from implementation limitations.
For example, macro-like intent reuse is a requirement; introducing a new construct
instead of extending trait/carry is a design choice.

Preserve these meanings across the alternatives:

- State reusable meaning and constraints once; expansion must not lose guarantees.
- Intent bundles introduce companion declarations, not necessarily nested values.
- Types, intents, predicates and modules are distinct compile-time parameter kinds.
- Qualified identities survive composition; selective visibility does not discard
  dependencies or change declaration-site bindings.
- Missing members, explicit null and non-null values remain distinguishable.
- Queries and live questions remain read-only; mutations have explicit contracts.
- Authority, preconditions, effects and returns have distinct meanings. Atomic
  guards cannot degrade into application-side checks followed by unguarded writes.
- Storage adapters preserve admitted semantics or refuse unsupported behavior.
- Public database I/O remains async-only for the current implementation scope.
  Future synchronous API targets may be represented without implementing them.

Accepted GARNS contracts are the baseline. A candidate that changes one must name
the change and the review it would require, rather than silently treating it as
already approved. No arbitrary host-language execution is introduced as a shortcut
for declaring predicates or data invariants.

## Feature areas

The initial scope is seven active areas, targeting 28 option dossiers. Each dossier
must cover the area's subrequirements, or explicitly show why it cannot meet them.

| Area | Requirements and design questions | Register |
| --- | --- | --- |
| Relationship vocabulary | Target deletion behavior, reference identity, optionality, joint uniqueness; clarity of declarations without SQL knowledge. Retain deletion as the preferred wording while comparing broader forms. | L1 |
| Reusable value constraints | Intent-level invariants, constraints across companion values, refinement composition, presence rules and validation timing. | L2 |
| Intent bundles | Macro-like expansion, trait reuse versus another abstraction, repeated use, naming, collision handling and propagation of constraints. | L3 |
| World and targets | Semantic world versus generation and deployment; persistence selection; language and API execution-style variants; one authoritative configuration. | L5 |
| Document value semantics | Exact recursive values, missing versus null, exact numbers, unknown-field preservation, original bytes versus meaning, and typed access. | L6 and Pyrocat domain requirements |
| Parameterized modules | Type, intent, predicate and module parameters; contracts, selective composition, qualification, instance identity and evolution. | L7 |
| Mutation contracts | Inputs, authority, expected-state guards, effects, returns, atomicity, immutable data and permitted transitions; relationship to existing verbs. | L8 |

L4, general collection-valued intents and collection invariants, remains an
unapproved extension. Sequences and mappings inside document values are in scope;
that does not automatically authorize a general collection-intent feature.

Audit the rest of the language for interactions: modules/imports, traits, carriers,
families, keys, references, query/question algebra, scope, evolution and generated
surfaces. Do not turn every keyword into another four-option exercise. Record any
additional fundamental requirement separately for a scope decision.

## Method

### Establish the baseline

Read the grammar, resolver, typed IR, runtime consumers, language reference,
limitations, accepted decisions and plans. For each requirement identify whether
it is implemented, declared but unconsumed, intentionally restricted, deferred,
or genuinely absent. Explain documented reasons for exclusion where available;
do not invent historical intent.

Carry forward the unfinished declarativity review as part of this audit. In
particular, check whether existing composition propagates constraints as well as
fields. Record defects separately from language-design proposals.

Bound the baseline audit to declarations and consumers relevant to these seven
areas, with one shared baseline pass and at most two targeted follow-up investigations
per area. This is not a repository-wide correctness audit. Permit at most two
small, single-question experiments per area, with no new service provisioning or
production implementation. Record unresolved claims when those bounds are reached;
ask before extending the investigation. An experiment must name the decision it
could change before it is run.

### Explore four alternatives per area

Develop each alternative from the shared requirements before ranking it against
the others. Four alternatives means different semantic organizations or authoring
models, not four spellings of the same construct or three deliberately weak foils.
Include a minimally disruptive route where it is viable, but give more substantial
redesigns equal consideration.

Independent exploration means avoiding an early preferred design that predetermines
every area. It does not require separate agents or models. Agent use, if later
authorized, must use the same brief and bounded deliverables, with preferences
withheld until the independent options are captured.

The operator explicitly accepts fewer than four credible alternatives when a
serious bounded search cannot find another. Before declaring a shortfall, revisit
the requirement decomposition and attempt a materially different mechanism, not
just another spelling. Record the approaches attempted, the reasons they fail and
the actual viable count. A failed approach is evidence, not a selectable solution.
Do not pad the comparison or claim parity. This authorized exception does not waive
requirement coverage or the hard semantic gates. Keep rejected approaches visible
so their tradeoffs are not repeatedly rediscovered.

### Use one option dossier format

Each dossier supplies:

1. The organizing idea, requirement coverage and its difference from the other options.
2. Compact proposed syntax and a plain-language semantic explanation.
3. A successful example and a refusal or ambiguity example from the common corpus.
4. Name binding, identity, typing, composition and evolution consequences.
5. Mapping to qualified IR, validation, generated APIs and adapter obligations.
6. Interaction requirements and incompatible choices in other areas.
7. Benefits, disadvantages, unresolved questions and likely failure modes.
8. Relative implementation and migration cost, with reasons and uncertainty rather
   than invented delivery estimates.
9. Evidence status: current behavior, demonstrated experiment, design argument or
   untested hypothesis. Proposed syntax is always labelled as such.

Put concise comparisons ahead of the full dossiers so the operator can scan first
and inspect details only where needed. Published language precedents, if used,
must be checked against primary documentation rather than recalled anecdotes.

### Compare interactions

Build an explicit compatibility matrix. Mark combinations compatible, requiring
adaptation, conflicting or unresolved, and explain nontrivial entries. Concentrate
on high-coupling relationships: intent bundles and constraints; module parameters
and identity; missing/null and mutation inputs; operation guards and invariant
timing; semantic guarantees and target capabilities.

Use that matrix to construct four coherent whole-language candidates. Each names
its selected options, necessary adaptations and remaining gaps. These are not all
possible combinations; they are representative designs that survive the strongest
interaction checks. Pairwise compatibility alone is not proof of whole-language
consistency, so each candidate must also be worked through end to end.
Include an option-to-candidate index. Explain why each viable option omitted from
all four candidates was omitted, and what a combination containing it would require.

### Evaluate whole languages

Rewrite the same examples under each candidate. Compare semantic expressiveness,
readability, reuse, predictable name resolution, enforceability, portability,
diagnostics, migration burden and implementation complexity. Use a qualitative
rubric with reasons; do not conceal tradeoffs behind a single numerical score.

### Declarativity filter

Use the operator-supplied **Declarative API Evaluator & Identifier**, internally
version 3, as the common lightweight qualitative filter. Its source is
`dev-docs/DeclarativeApiEvaluatorV2.md` in the separate `bizscad` repository; the
filename and the instrument's internal version differ. Record the source digest
used in the eventual comparison. Do not alter that instrument during this exercise.

This is an adaptation for design exploration, not a claim of completing the full
instrument, calibration, held-out corpus or authoring harness. Use design-stage
reasoning for proposed surfaces and distinguish it from inspection of the existing
implementation. Apply the following criteria consistently to individual options
and their combined designs:

- Meaning is defined independently of execution; descriptions can be inspected
  before effects, and meaningful order is explicit rather than ambient.
- Identify what the engine resolves or derives instead of asking the author to
  supply it. Keep gap richness and generativity separate from correctness.
- Examine predictable composition, retained constraints, explanation/provenance,
  escape containment and whether reusable compounds remain reusable parts.
- Evaluate representational and edit effort against the same examples, including
  defaults, diagnostics, evolution and the cost of implementing the engine.
- Name boundaries between surfaces, such as template expansion into constraints
  and operation contracts into adapters; assess their failure modes separately.
- For claimed error detection, name the decision procedure and a counterexample
  that would test it. An aspiration without a procedure remains unknown.

Use qualitative supported/concern/unknown assessments with cited evidence and
separate gate pass/fail/unknown results. Apply this declarativity checklist to each
candidate surface and cite the rule or example supporting each result:

| Gate | Pass condition |
| --- | --- |
| Explicit ordering | Meaning has no ambient dependence on execution or declaration order. Any meaningful order is explicitly declared and local to its stated scope. |
| Inspectable description | The program is data that can be inspected, transformed and compared before execution, not merely a sequence of effects. |
| Meaningful derivation | The engine demonstrably performs resolution, derivation or structural expansion beyond restating substrate operations. |

All three must pass to classify a surface as declarative; unknown leaves that
classification unresolved. These gates do not replace the separate semantic
fidelity, identity, constraint-preservation and atomicity requirements below.

Do not invent numerical correctness scores,
projected intervals without the instrument's required inputs, or measured frontier
membership. Full calibration, anchors, blind second-rater scoring, an authoring
harness and new benchmark suites are out of scope. The shared examples are a
comparison corpus, not a claimed held-out evaluation.

Retain failed and uncertain options in the record. A hard semantic failure prevents
selection; uncertainty is a stated proof obligation, not an automatic zero score.
Use the filter to expose weak proposals and tradeoffs, not to optimize a scalar or
silently rank every more complicated resolver above a simpler adequate design.

Semantic fidelity, retained constraints, unambiguous identity and enforceable
atomic operations are hard gates. Conciseness cannot compensate for failing them.
Distinguish valid guarantees with an unimplemented adapter from guarantees that
the candidate cannot coherently express.

Conclude with a preferred combination and credible alternatives, after presenting
the evidence. The operator remains free to select another set; explain which
adaptations that selection would entail.

## Common examples

- A relationship case covering target deletion restrict/cascade/detach, refusal
  of detach on a required reference, joint key uniqueness and standalone unenforced.
- One positive revision intent reused by unrelated carriers, including defaults
  and optional uses; invalid values must not bypass its rule.
- A lower/upper companion bundle with a shared bound invariant, used twice with
  explicit names; changing the bundle exposes all affected uses.
- Two modules each declaring ID, selective imports and aliases, and an imported
  resource whose references remain bound to the original ID.
- A versioned-document module parameterized by content type, an intent, a pure
  predicate and another module; two instances have deliberate identities.
- A document edit distinguishing omission, null, removal, false, zero and exact
  numbers while preserving unknown content and original-byte observations.
- Pyrocat propose/accept/discard, including first acceptance, equivalent acceptance,
  competing proposals, an accept/discard race, field restrictions and pinned evidence.
- A non-Pyrocat order or reservation operation with a cross-field constraint and
  guarded state transition, to expose application-specific assumptions.
- One unchanged semantic world targeting SQLite or PostgreSQL and an async Python
  API; future API variants are illustrative, not claims of working generators.

## Deliverables

Keep results in this repository's developer documentation:

| Artifact | Purpose |
| --- | --- |
| LanguageDesignExploration.md | Executive comparison, requirement coverage, evaluator-based filter, compatibility matrix, option-to-candidate index, four whole-language candidates and recommendation. |
| language-design-options/*.md | Seven focused files, each targeting four comparable option dossiers, with explicit viable counts and any authorized shortfall. |
| language-design-options/examples/ | Consistent example sets for all four candidate languages, explicitly identified as proposed, non-executable source. |
| LanguageChangeRegister.md | Updated links and decision status; no selected option marked accepted without operator approval. |

The comparison must identify which existing features remain unchanged, which are
replaced or consolidated, and which new obligations would require runtime work.
Include a dependency-ordered implementation outline for the preferred combination,
but do not implement it during exploration.

## Boundaries and completion

This request creates the proposal only. After operator approval, carry the bounded
exploration through to the complete comparison without asking for approval for
every individual alternative. Stop for a decision only if an unresolved requirement
would materially change scope; otherwise retain alternatives and label assumptions.

Exploration does not modify the grammar, production runtime, accepted schemas,
database contents or existing review approvals. Small disposable experiments may
check design claims after approval; their results are not production support.
Do not commit, push, launch agents or implement a selected design without the
corresponding authorization.

Completion means all seven areas have four credible options or the operator-authorized
bounded-search shortfall record, every stated requirement is accounted for, four combined
designs are evaluated against the shared examples, and the operator has a concise
decision guide. It does not mean the search was exhaustive or the revision accepted.

Next gate: operator review of this proposal, followed by authorization to explore.
Selection and independent review of the resulting language design precede any
compiler or runtime implementation.
