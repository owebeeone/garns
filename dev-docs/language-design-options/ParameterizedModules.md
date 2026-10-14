# Parameterized Module Alternatives

Requirement: type, intent, pure predicate and whole-module parameters; scoped names
such as A::ID and B::ID; selective visibility; no loss of original dependencies or
constraints. Runtime users and expected revisions remain operation inputs.

All options resolve names by identity, not textual substitution. Selection of an
export never prunes its semantic dependency closure. Instantiation has an explicit
identity policy: two named instances are distinct unless one explicitly aliases
the other. Equal arguments do not silently merge their data. Compiler code generation
may share implementation without sharing model identity.

## M1 Checked template specialization

```text
module Versioned<type T, intent Key, predicate Check, module Evidence> { ... }
module Public = Versioned<Subject, catalog::ID, Valid, Observations>
module Private = Versioned<Subject, catalog::ID, Valid, Observations>
```

Expand a generic module for each explicit instance, then resolve the specialized
module. Parameter kinds are checked at the boundary; required member names on a
module parameter are discovered from the template body and checked at instantiation.
No inferred structural compatibility exists beyond those explicit uses.

Valid: Public and Private have separate qualified resource identities while both
reference the supplied catalog::ID intent. Refusal: Evidence lacks Revision, Check
has wrong types, recursive specialization never terminates, or unqualified ID is
ambiguous. Definition-site references remain bound before argument substitution.

Cost medium/high; reuses the existing resolver after hygienic expansion. Errors may
arrive late and repeat per instance. Evolution maps instance identity, arguments and
template definition version. Fits B1/C1; weaker modular reasoning than signatures,
but legitimate and familiar as a design organization without claiming C++ compatibility.

## M2 Explicit module signatures

```text
signature EvidenceModel { export intent ID; export resource Revision }
module Versioned<type T, intent Key, predicate Check(T), module E: EvidenceModel> { ... }
module Public = Versioned<Subject, catalog::ID, Valid, Observations>
```

Check generic bodies against signatures before instantiation. The signature states
required exported declarations, kinds and invariant obligations. Exposing E::Revision
does not flatten E. Selection and renaming bind local aliases to stable identities.
Substitution must not weaken a promised constraint.

Valid: two independently implemented evidence modules satisfy the same contract.
Refusal: Revision exists but has an incompatible identity/reference role, or an
implementation claims a required predicate without enforcing it. Avoid general
logical implication solving: require matching named obligations, explicit witnesses
within a closed proof mechanism, or refuse unproved compatibility.

Cost high, best predictability for large reusable schemas. Fits B2 or B3/C2/C3.
Needs explicit sharing declarations if two parameters must name the same type or
resource; matching names are insufficient. Signature evolution and instance/schema
evolution are separate changes, both visible in the plan.

## M3 Constrained selective inclusion

```text
module Combined<module A: Source, module B: Source> {
  include A select {ID, Entry} as Left
  include B select {ID, Entry} as Right
  export Left::Entry, Right::Entry
}
```

Modules compose through selected exports, contracts and explicit refinements. This
is the closest to scoped inheritance, but no override changes inherited meaning
silently. An override requires an explicit replacement/continuity declaration and
proof that exported obligations still hold. Inclusion order cannot choose winners.

Valid: Left::ID and Right::ID coexist; Left::Entry retains its original Left::ID.
Refusal: both selected as bare ID, diamond inclusion with conflicting refinements,
or hiding a required dependency in a way that drops its constraint. Hidden dependencies
remain in the compiled closure; hiding means not author-visible, not nonexistent.

Cost high/very high; attractive for broad reuse but introduces more interaction rules.
Fits B3/R3/C3. Evolution must say whether including an existing module references its
existing identities or instantiates a fresh copy; this option defaults to references
and requires explicit instantiation for new identities. Namespaces alone are not copies.

## M4 Explicit module ports and linking

```text
module Versioned {
  input type Content
  input intent Key
  input predicate Valid(Content)
  input module Evidence: EvidenceModel
}
assembly Public {
  instance V: Versioned
  bind V.Content = Subject
  bind V.Key = catalog::ID
  bind V.Valid = ValidSubject
  bind V.Evidence = Observations
}
```

Separate reusable definitions from an explicit assembly graph. Bindings are data;
compiler derives dependency order and validates completeness before creating a model.
Port paths are qualified, and selected outputs are separately exposed. No service
discovery or implicit provider selection is involved.

Valid: reuse the same module definition in two named assemblies. Refusal: unbound
port, two bindings to one port, incompatible signature or a forbidden assembly cycle.
Referencing a supplied module retains its identities; a new instance creates new ones.

Cost high; verbose but explicit, strong fit with T4 and R2 named relationships.
Reduces template lookup surprises, adds an assembly layer for small programs. Changes
to bindings have first-class migration impact; an author cannot casually reconnect a
persistent instance to a new identity and call it a build-only change.

## Comparison

| Option | Gates and derivation | Strength | Concern | Cost |
| --- | --- | --- | --- | --- |
| M1 | P/P/P; hygienic specialization | Smaller conceptual addition | Late body errors | Medium/high |
| M2 | P/P/P; contract-checked substitution | Early predictable composition | Signature and sharing design | High |
| M3 | P/P/P; closure-preserving inclusion | Selective reuse/refinement | Override and diamond interactions | High/very high |
| M4 | P/P/P; binding graph resolution | Visible assembly and provenance | Wiring verbosity | High |

Projected only. Common mutants: swapped intent/type argument, wrong predicate arity,
two ID imports, captured local name, same-argument identity collapse, hidden dependency
loss and cyclic instantiation. Current named imports are the baseline; no generic
module syntax is implemented. Evidence: [grammar](../../grammar/garns.lark),
[resolver](../../src/garns/resolve.py), [reference](../../docs/DSL_REFERENCE.md).
