# Language Design Reassessment Against the Garns Vision

Status: design analysis, 15 October 2026. Reassesses the existing 28 options against [the vision](GarnsVision.md). No syntax, implementation, numerical score or candidate selection is accepted here.

## Main finding

The existing exploration recognizes useful derivation, but its whole-language preference gives substantial weight to local explicitness without fully testing whether rules and context could replace individual bindings. Candidate B remains a credible baseline; its preference is not established under the clarified vision.

The missing comparison is between author-enumerated connections and connections derived under declared rules, holding domain meaning and guarantees constant. This is distinct from comparing local versus standalone declarations, or familiar versus ambitious syntax.

M4 explicitly excludes provider selection; O1 explicitly requires step dependencies. Those are direct restrictions to reconsider. B4, R4 and C4 already describe rule-driven derivation and deserve complete scenarios alongside the existing candidates. Their greater reach creates real proof obligations, but nonlocality alone is not a defect. Conversely, O4 derives a change graph but does not thereby solve module wiring; Candidate D combines high mutation derivation with explicit assembly.

## Distinguish three kinds of information

| Information | Author responsibility | Possible engine responsibility |
| --- | --- | --- |
| Domain intent | State the required relationship, guarantee, outcome or meaningful distinction | Preserve it through resolution and execution |
| Connection and selection rules | Declare or select reusable rules where the language does not already define them; supply constraints that distinguish legitimate alternatives | Determine applicable declarations, dependency closure and concrete connections in context |
| Realization details | Supply genuinely external facts or choices that cannot be derived | Derive ordering, expansion, validation dependencies and supported execution plans |

Explicit references remain appropriate when they express a domain choice. Two compatible evidence providers can represent different authorities or datasets; type compatibility does not authorize substituting one for the other. The design question is which information is essential, not whether every binding can be removed.

Fresh versus shared persistent identity, authority, destructive intent and migration continuity cannot be guessed. They can be governed by reusable rules rather than repeated per connection, provided those rules preserve the intended distinctions.

## Reassessment of all seven areas

### Parameterized modules

Source: [M1–M4](language-design-options/ParameterizedModules.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| M1 specialization | Hygienic substitution and specialized name resolution | Every argument is supplied per instance, even where a declared environment could determine it | Retain direct application, but compare it with constrained contextual argument resolution. Late template checking is a separate issue. |
| M2 signatures | Contract checking, substitution and obligation preservation | Signatures constrain compatibility but the examples still supply every argument explicitly | Strong foundation for requirements and provider contracts; does not yet provide a selection mechanism. Signatures and contextual binding are compatible ideas. |
| M3 inclusion | Transitive dependency closure and retained declaration-site identity | Authors select visible exports and refinements | Selecting an API surface can be meaningful intent. Do not require listing dependencies already implied by selected exports. Its existing closure rule is a strength. |
| M4 ports | Dependency order and completeness of an authored binding graph | Every port has an explicit binding; provider selection is expressly excluded | Best place to compare explicit assembly with rule-derived assembly. Keep explicit binding available for semantic choices; evaluate context-based resolution rather than excluding it by definition. |

A proposed extension for comparison would let a module declare an evidence requirement and let a world select eligible providers under a named policy. Resolution would preserve provider identity and record why each binding was selected. No match, incompatible obligations or unresolved competing matches would produce a diagnostic. A choice among matches is permissible only under a declared selection procedure. This is a new design variant, not a capability already specified by M2 or M4.

### Intent bundles

Source: [B1–B4](language-design-options/IntentBundles.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| B1 traits | Fields and, as required by the proposal, inherited predicates | Repeated uses require per-member rename maps | Compare role-scoped expansion with manual renaming. A role such as opening is meaningful; spelling every resulting component name may be redundant. |
| B2 bundles | Complete component and predicate expansion from one use | Author chooses bundle and role per use | Already aligned with useful omission. Role selection distinguishes two uses and need not be inferred. Additional companion discovery is a separate extension. |
| B3 fragments | Export expansion with private dependency closure | Author selects the fragment to expand | Good when the choice identifies intended meaning. Compare derived required fragments against explicitly selected public fragments. Do not equate visibility with semantic closure. |
| B4 companion rules | Finite monotone closure of required declarations and predicates | Named rule activation is explicit | Directly aligned with rule-derived connectivity. Retain opt-in boundaries and finite-closure proof; evaluate its authoring benefit instead of discounting it merely for nonlocal consequences. |

The missing-invariant baseline defect strengthens the obligation to preserve expansion semantics. It does not establish that authors should enumerate expanded fields or predicates themselves.

### Relationships

Source: [R1–R4](language-design-options/Relationships.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| R1 inline links | Target resolution, joint keys and declared deletion consequences | Repeated policy and endpoint declarations | Concrete endpoints often express essential meaning. Reusable role policies could remove repetition without inferring relationships from names. |
| R2 named relationships | Carrier members and adjacency from external declarations | Every relationship still names its endpoints | Naming a connection separately does not reduce wiring. Useful identity and evolution benefits should be assessed independently of declarativity. |
| R3 contracts | Links, constraints and uniqueness from contract application | Repeated owner/target arguments and aliases | Strong reuse. Compare context-derived arguments where role and ownership contracts determine them; preserve explicit distinctions between otherwise compatible targets. |
| R4 integrity rules | Policy applicability, constraint graph and action ordering | Named role collections still delimit applicability | Important candidate for shared connection policies. Explore closed typed selectors under declared scope, with membership diffs and conflict checks. Arbitrary global matching is not required. |

Deriving a policy for a known relationship is different from discovering the relationship itself. A rule that selects references requiring detach must still establish that they are optional and preserve affected invariants. New selector membership can change deletion behavior and requires visible evolution treatment.

### Value constraints

Source: [C1–C4](language-design-options/ValueConstraints.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| C1 intent laws | Predicate propagation to every use | The same law may be copied across separately named intents | Keep role-local laws where appropriate; permit reuse through a shared predicate or value contract instead of copying. |
| C2 refined types | Refinement closure and shared validation | Authors name the refinement for each intent | Usually a meaningful validity declaration. Do not infer business validity from scalar type or naming convention. Derived validator dependencies should remain engine work. |
| C3 predicates | Typed argument substitution and obligation dependencies | Each invocation binds arguments explicitly | Position or role may determine some bindings under a typed contract. Compare that variant where it removes repetitive mappings, with diagnostics for swapped or ambiguous roles. |
| C4 theories | Rule applicability and affected-object validation plans | World selects a theory; rules select typed domains | Already addresses contextual propagation across carriers. Its concurrency and boundedness costs remain substantial; reduced locality does not invalidate it. |

Intent laws, refinements and named predicates need not be exclusive semantic universes. Whether they can share one law model should be evaluated without prematurely forcing a single surface form. Constraint selection and constraint enforcement are separate: choosing the right law does not prove runtime preservation.

### World and targets

Source: [T1–T4](language-design-options/WorldAndTargets.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| T1 separate declarations | World references and capability admission | Repeated world-to-build/deployment associations | Compare reusable assembly rules; external destinations and intended backend choices still need a declared source. |
| T2 world sections | Separate semantic/configuration records from one composition | Every target is listed locally | Primarily an organization choice. Context-derived assembly can coexist with a resolved world-facing target summary. |
| T3 profiles | Artifacts and defaults from reusable typed profiles | Explicit profile selection and parameters | More relevant under the vision than the small original target example suggests. Profile activation is a useful boundary; repeat applications and arguments may be derivable. |
| T4 target applications | Artifact order and invalidation | Each target constructor application is authored | An inspectable artifact graph need not be handwritten. Compare applications derived from a selected generation profile, preserving artifact identities and output-collision refusal. |

T1 and T2 may normalize to similar records, but that does not establish equal authoring burden. Separate the choice of presentation from the degree of target derivation. No contextual rule may silently weaken guarantees or authorize cross-store writes.

### Document values

Source: [V1–V4](language-design-options/DocumentValues.md).

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| V1 document scalar | Exact value operations and presence results | Repeated lookup paths, narrowing and patch construction | Small schema surface may move considerable work into authored reads and operations. Compare total authoring work rather than declaration size alone. |
| V2 structural schemas | Typed field access, validation and projections | Shape and presence declarations | These commonly state essential meaning. Derive accessors and patch behavior; retain the distinction between omitted and explicit null. |
| V3 format contracts | Typed views from a declared interpretation | Repeated projection/format selection | Context may select a revision-pinned interpretation under rules. It must never substitute the latest format silently. Strong candidate for deferred interpretation with stable provenance. |
| V4 value algebra | Visitors and generic structural operations | Authors may expose or traverse every structural node | A complete internal algebra does not require a verbose author-facing graph. Compare derived typed views and conveniences over the same semantics. |

This area is partly about representation and interpretation rather than connecting modules. Do not promote V4 simply because it exposes more structure, or reject it if that structure can remain an engine representation.

### Mutation contracts

Source: [O1–O4](language-design-options/MutationContracts.md) and the [Candidate B](language-design-options/examples/B-ExplicitContracts.md) and [Candidate D](language-design-options/examples/D-ExplicitAssembly.md) specimens.

| Option | What it already derives | Wiring to reconsider | Revised assessment |
| --- | --- | --- | --- |
| O1 compounds | Validation, failure propagation and transaction planning | Explicit steps and step dependencies | Derive dependencies from named results where possible. Require explicit ordering only where it expresses semantics beyond the data dependency graph. |
| O2 effects | Execution ordering from finite effects and result references | Authors still enumerate revision, evidence and decision effects | Good intermediate level, not the endpoint of derivation. Compare reusable effect contracts that derive required companion effects and bindings. |
| O3 transitions | Admission and legal outcomes from declared states | Outcome facts and case partitions remain authored | Useful if domain transitions determine effects through reusable laws. Explicit cases can encode genuine intent; do not assume all can be inferred. |
| O4 desired state | A bounded change graph under identity and preservation rules | Matching rules, desired facts and permitted region | Closely aligned with deriving realization. Evaluate narrower desired-state contracts without requiring M4 assembly, V4 values or the rest of Candidate D. |

Candidate B's acceptance example still spells out creation of a revision, evidence pins and a decision. The compiler orders those effects, but does not discover the whole acceptance topology. A higher-derivation alternative would declare acceptance meaning once and derive those companion facts under a reusable domain contract. That contract must define exact evidence, equivalent versus changed outcomes, protected guards and retry behavior. An unexplained helper name would only hide manual work.

## Consequences for the whole-language candidates

| Candidate | Revised position |
| --- | --- |
| A | Useful lower-change comparison. Explicit arguments and steps limit omission, although trait and predicate propagation already provide real derivation. Proximity to the baseline is not evidence of correctness. |
| B | Retain as a baseline for finite derivation. Reassess repeated module bindings and effect enumeration before preferring it. Contract checking does not require manual assembly. |
| C | Reusable contracts and preserved closure deserve more attention. Inclusion/refinement conflicts remain real; compare contract application burden against the wiring it eliminates. |
| D | Separate mutation planning from explicit assembly and exposed value machinery. High O4 derivation does not compensate automatically for M4's authored bindings. |

The existing four combinations do not adequately isolate contextual assembly, companion closure or shared rule application. A blanket switch from B to D would therefore miss the central question.

## Next comparison to prepare

The proposed specimens are now written in [Contextual Binding and Companion
Effects Comparison](language-design-options/examples/ContextualBindingAndCompanionEffects.md).
They remain unexecuted design examples; the evidence requirements below still apply.

Create a paired design specimen, rather than selecting another complete language bundle immediately. Use a common contract with three variations:

1. Manual binding and finite authored effects, using B and M4 as reference points.
2. Contract-constrained contextual binding with the same effects, isolating assembly derivation.
3. The same contextual binding with reusable companion-effect or bounded desired-state rules, isolating operation derivation.

Exercise at least these situations:

- One eligible evidence provider, two eligible providers and no eligible provider. A context must not silently redirect a semantic dependency.
- Two fresh module instances sharing some supplied identities. Derived binding must not collapse instance identity.
- Two bounds roles and transitive companion requirements. Closure must preserve both laws and reject collisions or unbounded role creation.
- Acceptance with equivalent content, changed evidence and a competing decision. Derived effects must preserve the full existing operation laws.
- A provider or rule-set change across generations. The plan must expose changed connectivity and distinguish semantic change from physical remapping.
- The stock-reservation case, to expose dependence on Pyrocat-specific assumptions.

For each variation, record what the author supplies, what the engine derives, the resolution procedure, ambiguity behavior, explanation and evolution obligations. Keep authority, identity and expected outcomes fixed. Report authored decisions and repeated bindings, not only token counts.

This would supply new design evidence, not measured correctness. Execution, independent oracles and held-out authoring tasks remain necessary for measured claims under the evaluator. The current reassessment is inspection-based and assigns no scores or frontier membership.

## Provisional direction

Preserve the ability to express an individual binding when it communicates a genuine choice. Add candidates where reusable rules and declared context determine those bindings when the choice is already implied. Prefer neither maximum manual explicitness nor maximum automatic derivation in advance: compare how much legitimate intent each surface expresses, how much redundant work it removes and how reliably its engine can preserve and explain the result.
