# C5 Combined intent, type and predicate constraints

Status: combined candidate captured from the operator's Workbench discussion on
16 October 2026. The operator's direction is to combine C1, C2 and C3, use trait
terminology and exclude C4's model-wide theory approach from this choice. The
specimen remains proposed syntax, not an accepted grammar or implementation.

## C5 Combined intent, type and predicate constraints

Keep C1's direct intent invariant as the preferred simple authoring form. Add C2's
named constrained value types for reuse across distinct intent identities and C3's
named, pure predicates. Use trait rather than bundle for companion expansion.
These forms coexist and lower through one constraint/validation mechanism.

```text
predicate Positive(value: Integer) = value > 0
predicate Ordered(lower: Integer, upper: Integer) = lower <= upper

// C1: the simplest direct form remains preferred for a one-off rule.
intent revision_number: Integer { invariant value > 0 }

// C2: reuse value validity without merging domain intent identities.
type PositiveRevision = Integer where Positive(self)
intent version_number: PositiveRevision

// C3: these two declarations illustrate explicit and abbreviated application.
intent sequence_number: Integer requires Positive(value)
intent generation_number: Integer requires Positive

intent lower: Integer
intent upper: Integer
trait Bounds {
  use lower
  use upper
  requires Ordered(lower, upper)
}

// Proposed trait shorthand: requires Ordered
// Argument derivation for a multi-parameter trait predicate remains open.
```

In a value-constraint position, an omitted argument of a unary predicate denotes
that constrained value. The explicit and abbreviated forms must elaborate to the
same predicate application, retain its identity/provenance and use the same
validation path. This is not a search for arbitrary surrounding names. Type
compatibility is checked; missing or ambiguous binding refuses.

The operator also proposed naming Ordered alone on the trait. Keep that as an
open shorthand question: should a trait supply a structured self argument, or
should declared semantic parameter roles map to companion members? Neither rule
is selected here. For now the executable meaning of the specimen uses explicit
Ordered(lower, upper); no general structural or same-name argument inference is
admitted by this example. Collection behavior is also outside this choice.

The compiler conjoins applicable type and intent constraints without source-order
override or weakening. Predicate declarations remain pure, typed and bounded;
value validity cannot depend on caller authority, the clock or arbitrary mutable
state. A refined value type does not automatically create theorem-based subtyping;
nominal identity, aliases and checked conversion remain design questions.

Valid: direct, named-type and named-predicate forms enforce the same positivity
law; distinct intents reuse the predicate without sharing their domain identities.
Refusal: zero inputs/defaults, weakening inherited guarantees, incompatible unary
predicate parameters, or ambiguous implicit trait argument binding. A stronger
constraint needs explicit validation/migration of existing values. One shared
mechanism must enforce creation, mutation, defaults and migration; shorthand must
not create a weaker validation route.

Open issues: final grammar/spelling and the type-value placeholder; exact
refinement identity/conversion rules; trait-level predicate argument derivation;
constraint provenance/deduplication and diagnostics; inherited conjunction and
migration obligations. C4's theory approach is excluded by the operator's stated
direction, while the original C1-C4 records remain historical alternatives.

This candidate has no passing compiler/runtime evidence. It is a design specimen
for comparison and refinement in the Workbench. See [the original alternatives](ValueConstraints.md).

## Operator follow-up: defer trait argument binding

The operator subsequently directed that the abbreviated trait predicate form be
included in the intended syntax, marked **not implemented**, and that its argument
binding rule be decided only when a concrete use requires it. Do not resolve the
structured-self versus companion-parameter question speculatively.

This reserves the surface form without claiming parser/compiler/runtime support.
Until binding and enforcement exist, an implementation encountering the form must
report that it is unimplemented; it must not silently ignore the predicate or
produce an executable result that purports to enforce it. No compiler changes are
authorized by recording this design direction. The original specimen above remains
the initial C5 publication; the follow-up is recorded in its Workbench discussion.
