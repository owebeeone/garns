# GARNS Language Design Exploration

Status: completed design comparison for operator selection. These proposals are
not accepted grammar, implemented APIs or measured correctness claims. No production
compiler/runtime files or databases were changed during this exploration.

## Findings first

The strongest opportunity is not shorter keywords. It is to make reusable declarations
carry their complete guarantees, and to derive a guarded atomic operation from declared
effects instead of repeating application logic. Generic modules help when their
identity and substitution rules are explicit; broad implicit inheritance would undo
much of that benefit.

**Provisional preference: Candidate B, Explicit Semantic Contracts.** It combines
local relationship declarations, reusable refined types, flat intent bundles, typed
module signatures, structural document values, finite atomic effects and clearly
separated world sections. It derives meaningful behavior without requiring a general
solver or reconciler. This is a design judgment, not a measured win.

Candidate A is the lower-change alternative. Candidate C is worth choosing if reusable
domain contracts and workflows dominate. Candidate D is an ambitious alternative
when desired-state authoring justifies a substantially larger engine and proof burden.

## Deliverables and reading order

- [Option index](language-design-options/README.md): seven area files, four alternatives each.
- [Baseline audit](language-design-options/Baseline.md): current support, deliberate limits and one reproduced defect.
- [Common examples](language-design-options/examples/README.md): fixed domain and case set.
- [A](language-design-options/examples/A-Incremental.md), [B](language-design-options/examples/B-ExplicitContracts.md), [C](language-design-options/examples/C-ContractComposition.md), [D](language-design-options/examples/D-ExplicitAssembly.md): comparable whole-language specimens.
- [Shared operation laws](language-design-options/examples/OperationLaws.md): precise meaning behind abbreviated operation examples.

There are 28 credible design alternatives in this comparison; no shortfall exception
was needed. Credible means sufficiently specified to compare, not implemented or
proven. Four combinations sample the design space; the comparison is not exhaustive.

## Baseline and scope decisions

Current grammar already provides typed intents, references, shared traits, named
imports, queries/questions and partial mutation declarations. Some metadata is parsed
but unconsumed. In-memory resolution reproduced a trait containing two fields and one
invariant whose consuming resource receives both fields but zero invariants. This is
an implementation defect, not an argument against the intended composition model.

The existing backend plan deliberately postponed grammar expansion and complete verb
execution. Its accepted authority, commit-knowledge, governed-write and physical-binding
contracts remain obligations. Changing invariant timing, generic identity or operation
planning requires explicit amendments; accepted headers or an illustrative example
do not authorize silent changes.

All candidates preserve static query versus live question, qualified identities,
read-only reads, external identity providers, guarded durable changes and adapter
refusal when guarantees cannot be met. Broad collection-intent features remain out
of scope; recursive sequences/maps inside exact document values are in scope.

## Evaluation method

The operator supplied the instrument titled **Declarative API Evaluator & Identifier**,
internally v3, stored as `dev-docs/DeclarativeApiEvaluatorV2.md` in the `bizscad`
repository. The version read has SHA-256:

```text
20a72d189d1ad032a9f0ab9bbfc1b63636cade0062c1d05bbae0383e7fb0e815
```

This comparison uses a lightweight adaptation, not a completed evaluator scorecard.
No calibrated scores, measured frontier, numeric correctness interval, held-out
coverage or model-authoring performance is claimed. The examples were visible during
design. Self-authored examples are not an independent correctness oracle.

Each option supplies three projected gate arguments: explicit/local ordering,
inspectable descriptions and meaningful engine derivation. All 28 are designed to
pass under their stated restrictions; that deliberately excludes arbitrary callback
escape hatches, textual macro substitution and last-import-wins semantics. Their
quality differs in what is derived, how predictable it is, and what the engine must
prove. Passing these gates is not sufficient for selection.

For correctness, distinguish an intended check from a specified decision procedure.
Examples include exact signature matching, finite effect conflict detection and
explicit case partitions. When a design would need unrestricted implication solving,
unbounded closure or nondeterministic matching, it refuses or marks that extension
unknown rather than claiming a future compiler will somehow solve it.

## Whole language comparison

| Candidate | Selected options | Useful derivation | Main concern | Relative change |
| --- | --- | --- | --- | --- |
| A Completed existing constructs | R1 C1 B1 T1 V1 M1 O1 | Predicate propagation, hygienic specialization, guarded step plans | Authors still wire effects; late template errors | Medium language change; high runtime work |
| B Explicit semantic contracts | R1 C2 B2 T2 V2 M2 O2 | Refinement closure, signature substitution, flat bundle expansion, finite effect dependencies | Keeping the shared type/predicate/effect core small | High |
| C Contract driven composition | R3 C3 B3 T2 V3 M3 O3 | Contract inclusion, typed projections, transition admission | Overlapping contract/refinement rules and workflow bias | High/very high |
| D Explicit assembly and desired state | R2 C2 B2 T4 V4 M4 O4 | Artifact assembly and deterministic change-plan derivation | Matching/preservation safety and value-graph cost | Very high |

| Criterion | A | B | C | D |
| --- | --- | --- | --- | --- |
| Reuse without copying laws | Supported by completed traits | Supported by bundles/refinements | Supported by contracts/exports | Supported by bundles/ports |
| Name predictability | Concern: errors at specialization | Strong explicit signatures | Concern: inclusion/refinement combinations | Strong explicit ports, more wiring |
| Mutation authoring | Explicit bounded steps | Finite declared effects | Declared legal transitions | Desired final fragment |
| Error explanation | Step and origin trace | Effect dependency and type trace | Contract/transition proof trace | Match and preserve/replace plan required |
| Escape containment | Closed predicates required | Closed predicates/effects required | Codec boundary needs independent evidence | No arbitrary reconciliation hooks admitted |
| Non-Pyrocat fit | Broad but manual | Broad finite operations | Strong workflows; bulk ergonomics uncertain | Strong reconciliation; small edits verbose |
| Implementation certainty | New consumers still unproved | New semantic core unproved | Contract implication explicitly bounded | Planner/large values least evidenced |
| Useful declarativity | Lower engine burden, more author wiring | Balanced derivation and visible contracts | Higher reusable policy machinery | Higher plan derivation, more hidden-work risk |

No candidate dominates all dimensions. D is not preferred merely because its engine
does more. A is not correct merely because it is closer to current source. B is the
best provisional balance for the stated requirements, pending an actual reviewed
language design and implementation evidence.

## Interaction matrix

This covers all 21 pairs of feature areas. It is a conditional design matrix, not
an exhaustive proof of every option product. `C` means compatible under the shared
laws; `A` requires the named adaptation; `X` identifies a semantic conflict that
must not be combined; `U` is unproved capability or cost.

| Pair | Compatibility and required decision |
| --- | --- |
| R / C | C: all relationship forms can carry predicates. A: R4+C4 should share one rule identity/algebra. X: deletion that leaves an invalid owner without refusal or repair. |
| R / B | C: qualified expanded references. A: R3+B3 share contract instantiation. X: bundle expansion silently joins unrelated key groups or drops deletion policy. |
| R / T | C: targets realize reference guarantees. A: declare capabilities for cascades and affected-state validation. X: backend choice weakens enforced references silently. |
| R / V | C: values and reference identities remain distinct. A: V4 node sharing must not create observable carrier identity. X: treating arbitrary document IDs as enforced links. |
| R / M | C: reference targets retain qualified origin. A: R2+M4 assemble external declarations before checking. X: rebinding inherited references to a local same-name ID. |
| R / O | C: delete closure is an effect obligation. A: R4+O4 need a single normalized action plan. X: independently executing cascades outside the guarded transaction. |
| C / B | C: C1/B1, C2/B2 and C3/B3 natural pairings. A: carry constraints through expansion with origin mapping. X: field-only expansion. |
| C / T | C: capability checks derive from semantic predicates. U: each target's affected-object guarantees. X: omitting unsupported predicates on a chosen target. |
| C / V | C: C2/V2 and C3/V3 align. A: C1/V1 needs typed document access. X: absence skipping a predicate that must examine explicit null. |
| C / M | C: constraints survive substitution. A: C3 predicate parameters require typed signatures. U: general predicate implication, deliberately not promised. |
| C / O | A: every option specifies input versus final-state invariant timing and protected read sets. X: preflight-only guard or unchecked dependent owners. |
| B / T | C: expansion precedes target lowering. A: target changes must not alter expansion identity. X: backend-selected companion fields changing domain meaning. |
| B / V | C: flat bundles and nested values are separate. A: generated API naming must distinguish them. X: a bundle instance unexpectedly allocates an identity-bearing object. |
| B / M | C: B1/M1, B2/M2, B3/M3. A: B4 needs finite closure after specialization. X: visibility filtering removes required companions. |
| B / O | C: operations consume resolved members. A: optional whole bundles need an atomic all-present/all-absent rule. X: partial update bypasses cross-companion validation. |
| T / V | C: value fidelity fixed across targets. U: exact-number operators and large-value profiles. X: target rounds numbers or truncates unknown content. |
| T / M | C: T2/M2 and T4/M4 clear. A: T3 profiles require one conflict system. X: import order selects a destination or generated artifact name. |
| T / O | C: language effects independent of target. U: transaction capability per adapter. X: multi-target generation interpreted as distributed atomic writes. |
| V / M | C: Content is a typed parameter. A: V3 carries format version/projection obligations. X: a module erases null/presence distinctions when specializing an API. |
| V / O | A: all options share Keep/Remove/Set and exact identity. U: V4/O4 resource cost. X: absent patch entries become deletion or equivalence ignores evidence. |
| M / O | C: qualified operations keep their authority/guards. A: reusable effects require explicit signatures and no nested independent commit. X: imported mutation bypasses owner module constraints. |

Whole-candidate walkthroughs also check multi-way interactions: generic bundles with
nullable members under an atomic update, format projections pinned to a template
instance, and a target switch with unchanged identity and operation guards. These
are reasoned analyses, not proof from executing the proposed language.

## Every option accounted for

| Options | Used in candidates | Omitted option rationale or adaptation |
| --- | --- | --- |
| R1 / R2 / R3 | A,B / D / C | R4 omitted: global integrity-rule organization adds a second nonlocal rule layer. A variant using R4+C4 must unify rule identity and explain affected deletion closure. |
| C1 / C2 / C3 | A / B,D / C | C4 omitted: broad constraint theories require dependency/concurrency machinery beyond these combinations. A specialized fifth profile could pair C4+B4+R4, with explicit finite domains and no unbounded solver. |
| B1 / B2 / B3 | A / B,D / C | B4 omitted: companion closure has less local predictability than explicit expansion for present examples. It remains viable for larger rule-driven models if explanation and finite closure are proved. |
| T1 / T2 / T4 | A / B,C / D | T3 omitted: reusable target profiles add indirection not exercised by the small target example. It can replace T2 in B/C without changing model semantics, with typed profile conflict checks. |
| V1 / V2 / V3 / V4 | A / B / C / D | All represented. |
| M1 / M2 / M3 / M4 | A / B / C / D | All represented. |
| O1 / O2 / O3 / O4 | A / B / C / D | All represented. |

Omission from a combined candidate is not rejection. Four combinations cannot exhibit
all tradeoffs; the index makes synthesis preferences inspectable rather than hiding
them in a recommendation.

## Requirement coverage

| Requirement | Location and unresolved design obligation |
| --- | --- |
| Clear deletion/reference/key vocabulary | Relationships; choice of inline versus named pattern remains open |
| Intent-level and multi-field invariants | ValueConstraints and IntentBundles; all require complete propagation and timing |
| Macro-like companion intent reuse | B1-B4; no option relies on nested storage to satisfy this |
| Independent target dimensions | T1-T4; future sync API notation only, async implementation scope unchanged |
| Missing/null, exact recursive values | V1-V4; actual codecs and canonical test vectors still needed |
| Types, intents, predicates, module parameters | M1-M4; each explicitly checks parameter kind and preserves identity |
| Qualified selective inheritance/composition | Module examples; dependency closure retained even when hidden |
| Authority, expected state, effects, returns | O1-O4 and OperationLaws; raw mutation bypass must be closed |
| Immutable facts and pinned evidence | Shared domain/operation laws; not achieved by adding an immutable keyword alone |
| One place to change shared intent meaning | Expansion/refinement provenance plus affected-generation plans; no silent migration |
| Domain-first, not PostgreSQL-first | All seven areas separate meaning from mapping; no database created |
| Individually reviewable files | Seven area documents plus separate four example files and this overview |

## Decision guide

Choose **A** if preserving current authoring style is most important and explicit
mutation steps are acceptable. It should still adopt strict constraint propagation,
clear guard timing and trustworthy absence semantics; those are not optional extras.

Choose **B** if the goal is a general declarative data language with predictable
reuse and operations. My recommendation is B, with the option of starting implementation
through A's smaller trait/compound compatibility surface and lowering both to B's
single semantic IR. That compatibility layer must not become a second runtime.

Choose **C** if expressing reusable domain contracts and state-change legality is
more important than minimizing abstraction count. Before selection, resolve exact
contract satisfaction and permissible refinement; do not defer those to implementation.

Choose **D** if desired-state mutation is a central authoring goal. Before selection,
require a convincing independent identity/preservation model and a bounded planner
prototype. Its cost is not justified solely by a higher derivation classification.

A plausible selective combination is B with B1 trait syntax instead of B2 bundle
syntax, provided repeated-role identity and inherited invariants are specified. Another
is B with T1 separate target declarations. Both preserve the main semantic organization;
neither requires choosing the same numbered alternative everywhere.

## Implementation outline after selection and design review

1. Freeze value, identity, role naming and substitution semantics; define current-to-new
   source migration and which accepted contracts require amendment.
2. Build one shared predicate/refinement and expansion IR. Repair inherited constraint
   propagation with canonical regressions, keeping defect fixes distinct from new syntax.
3. Define exact document values and patch semantics with independent round-trip vectors;
   qualify limits using realistic inventory size before promising support.
4. Add module contracts/instantiation and explainable resolution; verify collisions,
   hidden dependencies, repeated instances and migration continuity.
5. Add operation effect planning, authority and protected guards against the accepted
   transaction API. Prove atomicity, immutable routes and uncertain-commit behavior.
6. Normalize world/build/deployment configurations to separate identities and capability
   admission. No adapter silently approximates an unsupported semantic feature.
7. Qualify complete examples on supported adapters and generated APIs; preserve query/
   question behavior, ledger laws and evolution guarantees through integration tests.

This sequence is a dependency outline, not permission to implement. Backend/runtime
development can continue against accepted contracts, but new language claims need
their own reviewed interfaces and real execution evidence.

## Evidence limits and verification

The exploration used local GARNS source, docs, accepted scope records, the supplied
evaluator and the Pyrocat domain requirements. It did not import claims about other
languages from memory as evidence. No external-language precedent is needed for the
four mechanisms to be compared here.

One bounded resolver experiment reproduced the inherited-invariant gap. All other
new-language correctness arguments are design-stage analysis. The report does not
claim runtime validation, calibrated scoring, an exhaustive search or an independent
review of the resulting options. The earlier independent GO covered the exploration
proposal, not these results.

Mechanical checks verify local document links, seven areas with four option headings
each, four candidate example files, no absolute machine paths in new documentation
and whitespace consistency. These checks do not validate proposed syntax or semantics.
