# Reusable Value Constraint Alternatives

Requirement: positivity belongs with the meaning of a revision number; a shared
lower/upper relationship travels with its bundle. Resource-specific laws remain
at the resource. Existing pattern/length metadata must not remain unenforced.

All options distinguish value validity from operation preconditions. A value rule
cannot inspect clock, caller identity or arbitrary mutable state. Cross-reference
rules require an affected-object dependency plan or explicit capability refusal.

## C1 Invariants directly on intents

```text
intent revision_number: Integer { invariant value > 0 }
trait Bounds { use lower use upper invariant lower <= upper }
```

Add one value binding to intent predicates. Every use inherits the conjunction of
the intent's invariants; the carrier gets substituted predicates with origin data.
Bundled predicates bind companion names at declaration time. Type meaning remains
the current base type plus intent identity, not a new refinement type universe.

Valid: revision_number used by two unrelated carriers, both rejecting zero. Refusal:
a default of zero, or a predicate referring to another carrier's undeclared field.
Optional absence skips the value predicate; explicit nullable values need a declared
null policy. Presence laws are separate, so skipping is not accidental permission.

Cost medium: grammar/IR additions are small, enforcement across writes and migration
is not. Fits B1/R1 and incremental evolution. Constraint strengthening produces a
validation/migration obligation; it cannot silently invalidate stored values.
Weakness: independently named intents cannot conveniently share the same refinement
without another predicate mechanism. Diagnostics can still name original intent/use.

## C2 Reusable refined value types

```text
type PositiveRevision = Integer where self > 0
intent revision_number: PositiveRevision
bundle Bounds { lower: Integer upper: Integer invariant lower <= upper }
```

Separate reusable value validity from the domain role supplied by an intent. Types
may refine types by conjunction; cycles refuse. Bundle predicates remain relational
because neither bound is independently valid or invalid without its companion.
Do not infer arbitrary theorem-based subtyping: exact type identity or an explicit
checked conversion establishes compatibility.

Valid: two differently named intents share PositiveRevision without sharing their
identities. Refusal: assigning an unchecked Integer to PositiveRevision, even if the
author assumes positivity; a checked construction may accept it after validation.
Defaults and transformed migration values pass the same constructor gate.

IR carries named refinement closures; generated APIs share validators. Cost medium/high;
existing newtypes need a clear relationship to refinement aliases and nominal identity.
Fits M2 typed parameters and V2 structural values. Potential boilerplate for one-use
types is offset by predictable reuse. Predicate language stays bounded and decidable
to type-check, without promising satisfiability proofs for every formula.

## C3 Parameterized predicate contracts

```text
predicate Positive(x: Integer) = x > 0
predicate Ordered(lo: Integer, hi: Integer) = lo <= hi
intent revision_number: Integer requires Positive(value)
bundle Bounds requires Ordered(lower, upper)
```

Predicates are named, pure, typed declarations. Intents, bundles and module parameters
refer to them; the compiler substitutes qualified arguments and computes obligation
dependencies. This prioritizes sharing laws, rather than introducing many value types.
Constraint invocation is data, not a callback into Python.

Valid: one module takes a predicate parameter with a declared signature. Refusal:
a predicate with wrong argument types, recursion outside the admitted algebra, or an
authority/clock lookup masquerading as value validity. Optional guards are explicit;
each predicate declares admissible arguments instead of implicitly swallowing null.

Cost medium/high; must avoid duplicating C2 validators behind different syntax.
Fits B3/M3 contracts; C1 can lower into it but should not create two meanings for the
same condition. Schema evolution records the predicate definition digest and affected
uses, not merely its unchanged name. Local readability suffers if trivial rules are
always indirect; permit inlining for explanations, not semantic copying.

## C4 Closed constraint theories

```text
theory RevisionRules {
  forall r in Revision: r.revision_number > 0
  forall b in carries(Bounds): b.lower <= b.upper
}
world Catalog uses RevisionRules
```

Declare integrity over typed sets; compiler derives each rule's affected objects and
validation plan. Restrict quantification to finite, declared domains and a typed,
side-effect-free algebra. This can express uniqueness and cross-object conditions
without restating them per carrier. No unbounded solver is implied.

Valid: an update to a referenced bound triggers validation of dependent owners.
Refusal: unbounded domain selection, unsupported aggregate semantics, conflicting
theory imports or an adapter unable to protect the read/write dependency set.
No source-order override is permitted; compatible rules conjoin.

Cost very high: global dependency tracking, bounded evaluation and concurrency
protection. Fits R4/B4; mixed with C1 requires one normalized constraint identity.
Migration is model-wide theory validation. Strongest expressive reach, weakest
locality; broad expressiveness may increase runtime refusal rather than useful reuse.
Proof obligations must separate satisfiability, type checking and runtime preservation.

## Shared validation boundary

All options must validate inputs/defaults and the operation's final affected state.
Intermediate private values may be staged inside a declared atomic effect graph;
they cannot escape or be read as accepted state. Current per-mutation validation is
not silently changed: transaction-final checks are an explicit runtime amendment.
Whether transient states are admitted must be fixed before a backend is qualified.

| Option | Gates and useful derivation | Concern | Cost |
| --- | --- | --- | --- |
| C1 | P/P/P; propagates intent predicates | Shared rules across distinct intents | Medium |
| C2 | P/P/P; derives refinement closure | Nominal versus refined compatibility | Medium/high |
| C3 | P/P/P; binds and specializes predicate contracts | Indirection and template interactions | Medium/high |
| C4 | P/P/P; derives affected-state validation | Boundedness and concurrency complexity | Very high |

Every correctness claim is projected. Mutants: zero default, missing predicate
dependency, changed target violating an owner, null passed to non-null predicate,
and a strengthening migration with invalid legacy data. No passing runtime is claimed.
See [baseline](Baseline.md), [engine](../../src/garns/engine.py) and
[invariant resolver](../../src/garns/resolve_read.py).
