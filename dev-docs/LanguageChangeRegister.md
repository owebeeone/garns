# GARNS language change register

Status: discussion proposals collected during the Pyrocat modeling exercise.
No grammar, runtime or accepted specification has changed. This is a growing list,
not an implementation approval or a replacement for the v9-6 scope decisions.

The proposed comparison process is in
[LanguageDesignExplorationProposal.md](LanguageDesignExplorationProposal.md).
It awaits operator approval before exploration begins.

## Purpose

Improve how authors declare data meaning, reference behavior and reusable value
constraints. The syntax should communicate semantics without requiring knowledge
of tables, columns or a particular database's constraint mechanisms.

## L1: Replace the link keyword end with deletion

Current syntax:

```garns
link owner -> Revision { end restrict key }
```

Proposed spelling, endorsed for this change list:

```garns
link owner -> Revision { deletion restrict key }
link base -> Revision { deletion restrict optional }
```

The deletion policy applies when the referenced target is deleted. Preserve the
three existing behaviors: restrict prevents target deletion while referenced;
cascade deletes the referencing object; detach removes the reference and therefore
requires an optional link. Key and optional remain independent modifiers.

Reason: end suggests process completion and does not identify deletion. The new
word makes the event explicit. This is a naming change, not a storage feature.

Before implementation: decide old-spelling compatibility and deprecation, then
update grammar, diagnostics, documentation and canonical fixtures together. Do not
silently reassign attributes during source migration. Retain standalone unenforced
semantics and its conflict with deletion actions.

## L2: Invariants on scalar intents

Requirement: a rule inherent to a value's meaning is declared with its intent and
inherited by every use. A revision number must be positive wherever it appears.
Resource invariants remain for relationships specific to an owning object.

Illustrative syntax only; value binding name is undecided:

```garns
intent revision_number : Integer "positive acceptance number" {
  invariant value > 0
}
```

Current language admits resource/member invariants, not this intent item. Existing
text pattern/length refinements and closed sets need one coherent validation model;
pattern and length currently lack runtime consumers. Do not add more declarations
that merely parse without enforcing their meaning.

Decisions: binding the current value; multiple predicates (propose conjunction);
composition with use-level rules; whether absence skips a value predicate for an
optional use; diagnostics naming the intent and failing use. Validation applies to
defaults, repairs, imports, mutations and migrations, not only generated setters.
Read/backend violations must report contract failure rather than silently coercing.

## L3: Macro-like intent bundles and shared invariants

Requirement, clarified by the operator: using one intent bundle introduces its
companion intents wherever it is used. Declare the companions and their shared
rules once; every use inherits them. This is semantic expansion into the owning
carrier, not a nested structured value, collection or separately identified object.
A range bundle could introduce lower and upper intents plus lower <= upper.

Existing trait/carry composition already expands uses and links. Assess whether
extending or clarifying that mechanism satisfies this requirement before adding
a competing construct. Expansion must propagate invariants as well as fields.
Macro-like means typed, qualified expansion, not arbitrary text substitution.

Decisions: bundle declaration and use spelling; companion naming and repeated use;
transitive expansion and cycle refusal; collision and override rules; inherited
key/default/optional policies; cross-companion invariant binding; diagnostics that
retain declaration and use locations; evolution when a shared bundle changes.
Presence rules and validation timing must be explicit. No new syntax is fixed yet.

Adapters choose the representation of the expanded meaning. Additional columns
are one possible relational mapping, not the definition of the feature.

## L4: Collection-valued intents and collection invariants

Separate, unapproved extension, not the operator's meaning of L3: a sequence or set of values, with
element rules and rules over the collection? Examples: every score is nonnegative;
a collection is nonempty; values are unique; an ordered sequence is monotonic.

Existing list_of support is restricted and does not admit collection shapes on
intents; nested constructors are also restricted. Inspect and deliberately amend
those rules rather than treating this as an already available extension.

Decisions: sequence versus set semantics, order/duplicate handling, element versus
whole-value predicates, quantification, absence versus empty, nested structured
elements, finite bounds and diagnostics identifying the failing element. Keep this
distinct from L3 until the intended scope is agreed.

## L5: Separate world semantics from build and deployment settings

Requirement: distinguish what a data system means and guarantees from how its
artifacts are generated and where it runs. The current world body mixes module
composition, durability, writer and scope contracts with generated target choices.
It should not read as an undifferentiated collection of compiler switches.

Proposed responsibility split, with syntax and exact placement still undecided:

- Semantic world: included modules, relationships across those modules, scope and
  isolation, and required durability and governed-write guarantees.
- Build/generation configuration: requested output languages and artifacts, such
  as the current generated python/rust selection.
- Deployment and adapter configuration: backend, location, pool and operational
  settings that realize the declared world contract.

Operator clarification: the world-facing configuration must also expose persistence
destinations, such as SQLite or PostgreSQL, alongside generated language targets
such as Python or Rust. These are distinct target categories, not one generated
list. Separating responsibilities need not require separate top-level declarations:
explicit sections or references associated with a world are a design option.
The current grammar already selects engine in a deployment; decide how that
selection is presented through the world without introducing conflicting sources
of truth. Listing a backend is not a claim that its adapter is implemented.
Whether a world can select multiple persistence targets for separate deployments
is distinct from writing to several stores at once; this proposal does not imply
replication, federated queries or cross-database transactions.

Operator clarification: target selection should leave room for multiple generated
API variants from the same model, for example Python synchronous and Python
asynchronous surfaces together. Keep language, API execution style and persistence
backend distinct dimensions. Adapter execution strategy is a further concern:
an asynchronous public API can use a synchronous SQLite driver behind a worker;
SQLite's storage semantics do not become a different data model. Avoid confusing
API execution style with SQLite's similarly named durability setting.

Current scope remains asynchronous public database APIs only. Synchronous API
generation is future design capacity, not an implementation or release obligation.
Future variants must preserve the same data and transaction semantics, have
unambiguous artifact names, and declare supported target combinations explicitly.
Unsupported combinations must refuse rather than silently substitute a blocking
implementation. A synchronous surface is not assumed to be a trivial wrapper
around the async API; ownership and event-loop interoperability require design.

Durability and writer rules affect observable behavior; do not silently turn them
into optional backend tuning. Scope deployment currently means deployment-wide
scope rather than a row-level scope path; preserve that meaning while reviewing
its wording. Audit quarantine retention and the remaining world items individually
instead of assuming that every operational-sounding declaration is a build option.

Decisions: separate declarations/files versus explicit sections; references from
build and deployment configurations to a world; compatibility with existing world
sources; which changes alter semantic identity versus generated artifacts or
deployment admission. Adapters must satisfy the world contract or refuse it, not
weaken it to match backend capabilities. No grammar change is approved here.

## L6: Distinguish missing from explicit null

Requirement: document values preserve an absent member separately from a member
whose value is null. The current optional/present/absent model, lowered to SQL NULL
by the SQLite implementation, does not provide this three-state document contract.
A Python missing sentinel is a target representation, not the language semantics.
Specify omission, explicit null and a present non-null value independently of
storage. Partial-update omission can mean unchanged; removing a member must be a
separate explicit effect. Decide allowed nullability and presence per value shape,
including defaults, predicates, serialization and migration behavior.

## L7: Parameterized modules and qualified composition

Requirement: reusable modules declare compile-time parameters for types, intents,
predicates and whole modules. An intent argument retains its qualified identity,
value type and constraints; it is not reduced to its underlying scalar. Module
arguments satisfy declared contracts and expose members through a parameter
namespace. Runtime inputs remain operation parameters.

The operator proposes template-style notation and selective composition of
parameterized modules. Consider explicit qualification such as A::ID and B::ID;
these spellings are illustrative and are not accepted by the current grammar.
The resolver already preserves module-qualified identities and named import
aliases. Build on those semantics rather than textual substitution.

Requirements for the design:

- Define parameter kinds, required contracts, substitution and instantiation
  identity. Distinct named instances must not accidentally share data identities.
- Select or alias names entering local scope; refuse ambiguous unqualified names.
- Preserve declaration-site bindings inside imported resources and predicates.
- Keep dependencies and constraints even when their names are not exposed locally.
- Specify nested instantiation, cycle refusal, diagnostics and schema evolution.
- Keep predicate parameters typed and within an admitted pure expression algebra,
  rather than arbitrary host-language callbacks.

Inheritance versus composition terminology and exact syntax remain open. These
features are proposed, not a claim that current modules accept parameters.

## L8: Declarative mutation operations

Requirement: modules declare named mutation operations alongside read-only query
and question declarations. Each operation distinguishes inputs, authority,
preconditions, effects, returns and its atomic boundary. Queries remain read-only.

Existing restricted, bulk, alias and compound declarations are resolved and
validated but have no executing or generated verb surface in the current baseline.
Extend or consolidate that model; do not introduce a parallel mutation system or
claim that adding declarations to catalog.garns alone implements this feature.

Semantic example: accepting a proposal requires authority for its document, a
pending proposal, an expected base that is still current, and validation matching
the exact candidate and pinned evidence. A changed acceptance creates a revision
and its evidence plus one accepted decision atomically. Equivalent acceptance
records a decision pointing to the existing revision. A competing acceptance or
discard cannot satisfy incompatible terminal outcomes. Returns identify the
outcome; they are distinct from the persisted effects.

Decisions and proof obligations:

- Typed inputs and result shapes, with explicit absence and null semantics.
- Operation authority and object scope, plus permitted field changes. Identity
  providers remain outside GARNS; a field input allowlist alone is not authority.
- Expected-state checks and effects enforced as one atomic operation, including
  concurrency protection rather than a separate application-side preflight.
- Preconditions versus resulting-state invariants, including when shared and
  cross-object invariants are checked and which dependent objects are affected.
- Allowed transitions and immutable/append-only data enforced through every
  admitted write route, not only a generated convenience method.
- Failure, retry identity, equivalent outcomes and unknown completion consistent
  with accepted GARNS transaction contracts; no independent retry mechanism.
- Backend-neutral effects and adapter capability refusal before side effects.

This is a language and runtime design revision, not only a naming amendment.

## Scope of the combined revision

The collected proposals now span reusable declarations, value semantics, operation
contracts and target configuration. Prepare a coherent design with clearly staged
implementation rather than treating them as one small grammar patch. Separate
existing-but-unconsumed semantics from genuinely new language features. Preserve
accepted runtime contracts unless an explicit reviewed amendment changes them.

## Naming observations without proposed semantic changes

- link is a reference-valued field; its name is the field name and its target is
  the referenced type. It need not be a physical foreign-key column in every target.
- All key-marked uses and links form one combined uniqueness rule, not independent
  uniqueness constraints. Keep this meaning explicit in author documentation.
- optional permits absence of the reference; it does not disable target validation
  when the reference is present.
- association declares a relationship with its own values and constraints. A table
  is one adapter representation. No rename for link/key/association is agreed.

## Design and proof sequence

1. Review names and value semantics before fixing grammar or implementation syntax.
2. Map each proposal onto qualified IR, validation, generated surfaces, queries,
   evolution and adapter obligations; refuse unsupported combinations explicitly.
3. Prove inherited intent constraints with canonical valid/invalid fixtures,
   including multiple uses and defaults. Prove bundle expansion preserves shared
   constraints. Collection changes require a separate scope decision.
4. Prove behavior through claimed target adapters without changing domain meaning.

Sources: docs/DSL_REFERENCE.md (Types, Intents, Carriers and Invariants),
docs/LIMITATIONS.md, docs/GARNS_DIRECTION.md (Language policy), and
dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md (scope). These proposals
need an explicit language-scope decision because the current backend iteration
preserves the ratified grammar.
