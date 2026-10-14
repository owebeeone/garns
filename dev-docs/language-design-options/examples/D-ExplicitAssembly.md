# Candidate D Explicit Assembly and Desired State

Choices: R2 C2 B2 T4 V4 M4 O4. Proposed notation throughout. This explores higher
engine derivation with explicit assembly, rather than mixing every most-generative
option into an opaque rule system.

## Model and reuse

```text
type PositiveRevision = Integer where self > 0
value Value = Null | Bool(Boolean) | Number(ExactNumber) | Text(Text)
            | Sequence<ordered Value> | Object<unique Text => Value>
bundle Bounds {lower: Integer; upper: Integer; invariant lower <= upper}
module Versioned {
  input type Content
  input intent Key
  input predicate Valid(Content)
  input module Evidence: EvidenceModel
  resource Document {use Key}
  resource Revision immutable {revision_number: PositiveRevision; content: Content}
  resource Proposal immutable {content: Content}
  resource Decision immutable {disposition: Disposition}
  relationship RevisionDocument {owner Revision as document; target Document; cardinality exactly_one; target_deletion restrict}
  relationship ProposalDocument {owner Proposal as document; target Document; cardinality exactly_one; target_deletion restrict}
  relationship ProposalBase {owner Proposal as base; target Revision; cardinality zero_or_one; target_deletion restrict}
  relationship DecisionProposal {owner Decision as proposal; target Proposal; cardinality exactly_one; target_deletion restrict}
  relationship DecisionResult {owner Decision as result; target Revision; cardinality zero_or_one; target_deletion restrict}
  unique Revision by document, revision_number
  unique Decision by proposal
  resource Window {use Bounds as opening; use Bounds as closing}
}
assembly Public {
  instance V: Versioned
  bind V.Content = Value
  bind V.Key = names::ID
  bind V.Valid = ValidCatalog
  bind V.Evidence = Observations
}
assembly Private {instance V: Versioned; bind V ports as Public.V arguments}
```

The last shorthand shares arguments, not instance identity. Evidence associations
and other common fields follow the domain table and named relationship form. The
value model has no observable storage node identities. Explicit model assembly
must retain all relationship and invariant dependencies when exporting V.

## Reads, desired effects and targets

```text
query history of V::Revision {
  given selected: V::Document
  where document is selected
  show revision_number, acceptance_fingerprint
  order revision_number
}
mutation Accept(p: Proposal, expected: optional Revision) {
  authority accept(p.document)
  require pending(p) and p.base is expected and current(p.document) is expected
  require validated_exactly(p)
  match existing Revision only when it is current(p.document)
        and its full_acceptance_identity equals acceptance_identity(p)
  desired atomic within p.document {
    accepted_revision(p) = current if equivalent else fresh next_number(expected)
    content(accepted_revision(p)) = exact_candidate(p)
    evidence(accepted_revision(p)) = exact_pins(p)
    decision(p) = equivalent or accepted as determined_by_identity
  }
  preserve existing revisions and all outside declared_targets
  returns decision(p)
}
mutation Discard(p: Proposal) {
  authority discard(p.document)
  require pending(p)
  desired atomic {decision(p) = discarded with result absent}
  preserve all_except decision(p)
  returns decision(p)
}
world CatalogWorld = Public.V
artifact Api = PythonAsync<CatalogWorld>
store Local = SQLite<CatalogWorld, LocalBinding>
store Server = PostgreSQL<CatalogWorld, ServerBinding>
```

Matching for acceptance is constrained to current identity, not an arbitrary old
matching revision.
Equivalent desired content must compare equal and generate no write to immutable
current data. Fresh acceptance appends; it never replaces the previous revision.
Omission from desired state has no deletion meaning.

## Same cases through this candidate

| Cases | Expression and consequence |
| --- | --- |
| E1 | Named relationships plus named uniqueness; policy conflicts refuse before plan derivation. |
| E2/E3 | Refined revision type and hygienic Bounds expansions preserve value rules. |
| E4/E5 | Explicit module ports and aliases retain original identity; two instances sharing arguments remain distinct. |
| E6 | Recursive value algebra makes missing entry versus Null node explicit; typed patches preserve untouched subtrees. |
| E7 | Deterministic identity rules derive finite create/preserve actions under atomic guards; shared laws remain mandatory. |
| E8 | Reserve declares a desired reservation and corresponding stock/version change in a bounded region; the planner cannot infer amounts not declared. |
| E9 | Typed target applications derive artifact dependencies; backend changes do not redefine domain meaning. |

## Where it succeeds and strains

The non-Pyrocat operation uses the same mechanism:

```text
mutation Reserve(s: Stock, expected: Integer, qty: PositiveQuantity) {
  authority reserve(s)
  require s.version = expected and s.available >= qty
  desired atomic within s {
    s.available = before(s.available)-qty
    s.version = expected+1
    fresh r: Reservation(stock=s, quantity=qty)
  }
  preserve all_except s.available, s.version, r
  returns r
}
```

Fresh is tied to this operation's retry identity, not to a new object on every retry.
The declared region explicitly includes the new reservation; it cannot touch others.

Explicit assembly keeps dependency and target choices inspectable while reconciliation
derives a change graph. Its largest risk is matching and preservation correctness,
followed by value-graph performance. More engine-derived work does not prove better
authoring: the assembly and desired-state explanation may exceed the code they replace.
This is a credible ambitious alternative, not the default recommendation.
