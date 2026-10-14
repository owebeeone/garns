# Declarative Mutation Alternatives

Requirement: state permitted changes once, including inputs, trusted authority,
expected state, effects and returns. Acceptance of a proposal must create a consistent
revision/evidence/decision or nothing. Scope and field authorization differ from an
input allowlist. Queries/questions remain read-only.

The four alternatives share the laws in [operation examples](examples/OperationLaws.md).
They differ in what the author describes: steps, effects, transitions or desired state.
All are static descriptions before execution, not embedded Python procedures.

## O1 Bounded declarative compounds

```text
compound Accept(p: Proposal, expected: optional Revision) atomic {
  authority accept(p.document)
  require pending(p) and current(p.document) is expected
  require validated_exactly(p)
  step r = Revision.mint(from p) when changed_identity(p)
  step d = Decision.mint(result = r otherwise current(p.document))
  returns d
}
```

Extend existing compounds with typed parameters, guards, conditional steps, returns
and authority. Step dependencies must be explicit; bounded, inspectable sequence
order can remain local. Compiler derives input validation, failure propagation,
reference binding, write effects and one transaction plan.

Valid: a decision depends on the selected revision result. Refusal: unbound earlier
step, conflicting writes, guard outside transaction or an effectful callback hidden
in a condition. An arbitrary loop or host-language step is not admitted.

Cost high despite familiar grammar: current verbs have no runtime. Incremental reuse
is strongest, generativity lowest because authors still wire most mutation steps.
Fits M1/B1/V1. Good explainability through a plan trace. Evolution preserves named
operation identity while versioning its complete intent and guards for replay.

## O2 Atomic effect contracts

```text
operation Accept(p: Proposal, expected: optional Revision) {
  authority accept(p.document)
  require pending(p) and current(p.document) is expected and validated_exactly(p)
  effects atomic {
    r = accepted_revision(p)  # new if full identity differs, otherwise existing
    create Decision(proposal=p, result=r, disposition=disposition_for(r))
  }
  returns Decision
}
```

Declare a finite set of typed create/update/delete/assert effects, with data references
that induce dependencies. The author states resulting facts rather than every ordering
step. `accepted_revision` above is a declared reusable effect fragment, not a magic
runtime builtin; its full definition appears in the common examples.

Valid: compiler orders revision creation before referencing decision and includes
evidence closure. Refusal: two effects assign incompatible final values, an unresolved
effect dependency, or a cyclic creation pattern unsupported by the target's admitted
identity-allocation strategy. Do not invent a solver to choose an arbitrary result.

Cost high; requires a small effect IR and complete affected-state validation. Fits
C2/B2/M2/V2; adapters choose execution details under the same atomic guarantee.
Less imperative than O1 without the general inference burden of O4. Diagnostics
must explain derived dependencies, protected read sets and original author effects.

## O3 State transition contracts

```text
transition Accept(p: Proposal) from Pending to Decided {
  input expected: optional Revision
  authority accept(p.document)
  guard current(p.document) is expected and validated_exactly(p)
  establish Accepted(p, accepted_revision(p)) or Equivalent(p, current(p.document))
  returns outcome
}
```

Model legal state changes and their object facts explicitly. Pending/Decided can be
derived from absence/presence of Decision, not a second mutable status field. Alternative
outcomes have disjoint exhaustive guards; they are not nondeterministic choices.
The compiler derives transition admission and disallows operations on immutable
facts outside their declared creation/removal rules.

Valid: Accept and Discard compete for the same Pending state. Refusal: overlap between
accepted and equivalent guards, a missing outcome branch, or an unconstrained transition
that rewrites historical revisions. General guard disjointness may be undecidable;
require a closed discriminator or explicit case partition rather than guessing.

Cost high/very high. Excellent for workflow laws, awkward for ordinary bulk updates
unless those can use reusable transitions without artificial states. Fits M3/C3/V3.
Evolution includes transition compatibility for pending objects and pinned operations;
state names changing do not justify rewriting old decisions.

## O4 Bounded desired-state reconciliation

```text
mutation Accept(p: Proposal, expected: optional Revision) {
  authority accept(p.document)
  require pending(p) and current(p.document) is expected and validated_exactly(p)
  desired within p.document {
    accepted_meaning = p.meaning_with_evidence
    terminal_decision(p) = accepted_or_equivalent
  }
  preserve all_except declared_targets
  returns terminal_decision(p)
}
```

Declare a desired model fragment and preservation boundaries. A deterministic planner
derives the minimal admitted change set using explicit identity/matching rules. It is
one bounded transaction reconciliation, not an autonomous background loop. Desired
state never authorizes deletion merely because data was omitted.

Valid: an already-equivalent meaning adds a decision without duplicating a revision.
Refusal: ambiguous identity match, conflicting desired facts, effects outside the
declared region, or a plan that rewrites immutable evidence. Matching rules must yield
one result; an underspecified optimization problem refuses.

Cost very high. Highest potential engine derivation, largest explainability and
correctness burden. Fits V4/R2/M4 if the value and identity model is explicit. Evolving
matching/default rules changes operation semantics and must be versioned. A dry-run
is useful explanation, but actual guards must still be rechecked atomically at commit.

## Comparison and required proofs

| Option | Gates and derivation | Benefit | Concern | Cost |
| --- | --- | --- | --- | --- |
| O1 | P/P/P; guarded transactional step planning | Builds on existing verbs | Authors still wire steps | High |
| O2 | P/P/P; dependency order from finite effects | Strong declarativity without general solver | Effect conflicts and final-state checking | High |
| O3 | P/P/P; transition admission and outcome derivation | Legal lifecycle visible | Workflow bias and case coverage | High/very high |
| O4 | P/P/P; derives change topology from desired facts | Least manual wiring | Matching, deletion and planner risk | Very high |

All authority and concurrency claims are unproved until runtime tests. Required cases:
two proposals on one base, accept/discard race, first acceptance, equivalent acceptance,
same content with changed evidence, unauthorized field replacement, replay with changed
intent, cancellation before effects and unknown completion after commit request.
An input list is not authorization, and idempotence is not proof of commit outcome.

Evidence: [verb grammar](../../grammar/garns.lark), [resolver](../../src/garns/resolve.py),
[runtime limitations](../../docs/LIMITATIONS.md), [A4 publication](../../docs/adr/A4-revision-publication.md)
and [A7 retry](../../docs/adr/A7-isolation-retry.md). Implementing any option requires
new consumers and reviewed API/plan amendments, not just a new keyword.
