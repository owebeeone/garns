# Intent Bundle Alternatives

The requested bundle is macro-like: companion fields and their laws appear at every
use. It is not a nested object or a collection. All alternatives require typed,
qualified expansion with source provenance, not textual substitution.

## B1 Complete trait and carry semantics

```text
trait Bounds { use lower use upper invariant lower <= upper }
resource Window { carry Bounds }
```

Retain the existing construct, repair invariant propagation and make trait expansion
the canonical reuse mechanism. For repeated use, add an explicit mapping such as
`carry Bounds rename {lower => start, upper => finish}`. The mapping introduces
member roles while preserving the originating intent identity; these two concepts
must not be conflated by an unqualified-name API.

Valid: Window inherits both fields and the predicate. Refusal: two mapped members
claim the same role with incompatible policy. Existing narrowing/conflict checks
extend to predicates and keys. No override can remove an inherited guarantee.

Cost medium; repeated uses need more than today's intent-keyed field model. Existing
single-use schemas remain closest to current GARNS. Traits are broad enough to include
links, which is helpful but can blur a value bundle with a resource role. Fits C1/M1;
an imported trait must bind its original intents, not local lookalikes. Expansion
origin maps support change impact and migration. Current missing invariants are a
defect to fix regardless of whether this becomes the chosen language design.

## B2 Explicit typed expansion bundles

```text
bundle Bounds {
  component lower: Integer
  component upper: Integer
  invariant lower <= upper
}
resource Window {
  use Bounds as opening
  use Bounds as closing
}
```

Bundle components become flat logical carrier members identified by bundle instance
and component. `opening::lower` is a role qualifier, not evidence of nested storage.
Each expansion gets the substituted invariant and component defaults/refinements.
No separate bundle object is allocated at runtime.

Valid: opening and closing bounds coexist with independent constraints. Refusal:
renaming opening::lower to a role already occupied by another declaration, recursive
bundle expansion, or dropping one required companion. Optional whole bundles need
an all-absent/all-present rule; optional components remain a separate contract.

Cost medium/high; a dedicated IR expansion node plus canonical flattening is required.
Better role identity than ad-hoc field renaming; introduces another declaration kind
unless traits are retired or precisely scoped to reference-bearing roles. Fits C2/M2,
also C1/M4. Evolution compares component identity and instance mappings so a shared
edit yields a complete affected-carrier report, not silent regenerated names.

## B3 Signature-governed module fragments

```text
module Bounds exports BundleShape {
  intent lower: Integer
  intent upper: Integer
  rule ordered: lower <= upper
}
resource Window { expand Bounds as opening }
```

Use one composition system: modules can export a closed bundle-shaped fragment.
An explicit signature distinguishes expandable members/rules from ordinary resources,
operations and private dependencies. Importing a module does not automatically expand
it; `expand` selects the declared fragment.

Valid: a parameterized bounds module supplies its exported fragment. Refusal: selecting
only lower while the selected bundle contract requires upper and ordered; selecting
an operation as a field fragment. Transitive private dependencies are retained without
being exposed as author-visible members.

Cost high initially, potentially lower long-term if generic modules are already
required. Strong fit with M2/M3 and C3; relatively heavyweight without signatures.
Canonical identity uses the module instance, export and expansion site. Evolution
must distinguish changed private implementation from changed exported meaning.
Concern: coupling simple field reuse to sophisticated module checking and instantiation.

## B4 Companion implication rules

```text
companion_rule Bounds {
  having lower in a carrier requires upper in that carrier
  invariant lower <= upper
}
resource Window { use lower with Bounds }
```

The author opts into a named companion rule set. Compiler computes a finite monotone
closure of required declarations, then attaches predicates. The rule names are explicit;
there is no ambient global rule that changes every future use of lower silently.
Only declaration addition is admitted, not overwriting, deletion or runtime effects.

Valid: lower brings upper and the relationship rule. Refusal: contradictory required
defaults, name collision, or recursive parameter expansion that generates unbounded
new roles. A finite cycle over the same declarations can terminate at a fixed point;
the compiler must prove that finite universe or refuse it.

Cost high; meaningful automatic closure reduces repetition but makes consequences
less obvious. Fits C4/R4 when they share a rule engine; poor fit with opaque inherited
overrides. Require an expansion explanation showing each introduced field and why.
Versioned rule-set membership and closure diffs are essential migration artifacts.

## Comparison

| Option | Gates and derivation | Primary advantage | Main risk | Cost |
| --- | --- | --- | --- | --- |
| B1 | P/P/P; trait expansion | Reuses existing abstraction | Role renaming extends current identity model | Medium |
| B2 | P/P/P; hygienic component expansion | Clear value-bundle semantics | Another construct unless traits are consolidated | Medium/high |
| B3 | P/P/P; signature-checked export expansion | One generic composition mechanism | Module complexity for small bundles | High |
| B4 | P/P/P; finite companion closure | Says only the initiating declaration | Nonlocal consequences and closure proofs | High |

The invariant-propagation probe in [Baseline.md](Baseline.md) is the only executed
evidence here. All four new semantics are unimplemented. Common tests must include
two instances, diamond composition, predicate rebinding, conflicting keys/defaults,
optional-group presence and a migration affecting several consuming carriers.
